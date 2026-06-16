import json
import structlog
from text_generation.backends import get_llm_backend, TextGenerationFactory
from django.conf import settings
from django.http import JsonResponse
from commons.base.views import BaseView, AuthenticatedView
from .models import StoryTransitionRecord
from .services.unfold_studio import UnfoldStudioService
from .constants import (StoryContinueDirections, CONTINUE_STORY_SYSTEM_PROMPT, CONTINUE_STORY_USER_PROMPT_TEMPLATE, AGENT_CHARACTER_SYSTEM_PROMPT, AGENT_CHARACTER_USER_PROMPT_TEMPLATE)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

log = structlog.get_logger("text_generation")

class GenerateTextView(BaseView):

    def validate_request(self, request_body):
        prompt = request_body.get('prompt')
        if not prompt:
            return False, "Prompt cannot be empty"
        return True, None

    def post(self, request):
        try: 
            request_body = json.loads(request.body)
            prompt = request_body.get('prompt')
            context_array = request_body.get('context_array', [])
            seed = request_body.get('ai_seed') or settings.DEFAULT_AI_SEED

            validation_successful, failure_reason = self.validate_request(request_body)
            if not validation_successful:
                return JsonResponse({"error": failure_reason}, status=400)

            backend = get_llm_backend()

            if not backend.is_generate_cached(prompt, context_array, seed) and not request.user.is_authenticated:
                return JsonResponse({"error": "Authentication required for uncached AI generation."}, status=401)

            result = backend.generate(
                prompt=prompt,
                context_array=context_array,
                seed=seed,
                hit_cache=True
            )

            return JsonResponse({"result": result}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class GetNextDirectionView(AuthenticatedView):

    def validate_request(self, request_body):
        required_fields = ['user_input', 'target_knot_name', 'story_play_instance_uuid']
        for field in required_fields:
            if not request_body.get(field):
                return False, f"Missing required field: {field}"
        return True, None

    def build_system_and_user_prompt(self, target_knot_data, story_history, user_input):
        system_prompt = CONTINUE_STORY_SYSTEM_PROMPT
        user_prompt = CONTINUE_STORY_USER_PROMPT_TEMPLATE % {
            'target_knot': target_knot_data.get('knotContents', []),
            'history': json.dumps(story_history, indent=2),
            'user_input': user_input
        }

        return system_prompt, user_prompt

    def parse_and_validate_ai_response(self, data):
        try:
            if data.startswith("```json") and data.endswith("```"):
                data = data[7:-3].strip()
            parsed_data = json.loads(data)

            probabilities = parsed_data.get('probabilities', {})
            if not isinstance(probabilities, dict):
                raise ValueError("Invalid probabilities format")
                
            required_directions = StoryContinueDirections.values()
            for direction in required_directions:
                if direction not in probabilities:
                    raise ValueError(f"Missing probability for {direction}")

            total_probability = int(sum(probabilities.values()))
            if total_probability != 1:
                raise ValueError(f"Total probability does not equal 1")

            return parsed_data
            
        except json.JSONDecodeError:
            log.exception("JSON decode error in AI response data")
            raise
        except ValueError:
            log.exception("AI response data validation failed")
            raise
        except Exception:
            log.exception("Unexpected error parsing AI response data")
            raise

    def determine_next_direction_details_from_ai_response(self, data):
        probabilities = data.get('probabilities', {})
        max_prob = max(probabilities.values())
        selected_direction = next(
            direction for direction, prob in probabilities.items()
            if prob == max_prob
        )

        if selected_direction not in StoryContinueDirections.values():
            raise ValueError("Invalid direction received")

        selected_direction_content = data.get(selected_direction.lower(), {})

        return selected_direction, selected_direction_content


    def get_next_direction_details_for_story(self, target_knot_data, story_history, user_input, seed):
        default_direction = StoryContinueDirections.NEEDS_INPUT
        default_content = {
            "guidance_text": "What would you like to do next?",
            "reason": "System failure"
        }

        try:
            backend = get_llm_backend()

            system_prompt, user_prompt = self.build_system_and_user_prompt(target_knot_data, story_history, user_input)
            response = backend.get_ai_response_by_system_and_user_prompt(system_prompt, user_prompt, seed, hit_cache=True, force_json=True)
            parsed_response = self.parse_and_validate_ai_response(response)
            direction, content = self.determine_next_direction_details_from_ai_response(parsed_response)

            return direction, content
            
        except Exception:
            log.exception("Exception in get_next_direction_details_for_story")
            return default_direction, default_content

    def save_story_transition_record(self, story_play_instance_uuid, previous_story_timeline, target_knot_data, user_input, ai_decision):
        StoryTransitionRecord.objects.create(
            story_play_instance_uuid=story_play_instance_uuid,
            previous_story_timeline=previous_story_timeline,
            target_knot_data=target_knot_data,
            user_input=user_input,
            ai_decision=ai_decision,
        )


    def post(self, request):
        try: 
            request_body = json.loads(request.body)
            seed = request_body.get('ai_seed') or settings.DEFAULT_AI_SEED
            user_input = request_body.get('user_input')
            target_knot_name = request_body.get('target_knot_name')
            story_play_instance_uuid = request_body.get('story_play_instance_uuid')
            log.debug("GetNextDirectionView.post", target_knot_name=target_knot_name,
                      story_play_instance_uuid=story_play_instance_uuid, seed=seed)

            result = {}

            validation_successful, failure_reason = self.validate_request(request_body)
            if not validation_successful:
                return JsonResponse({"error": failure_reason}, status=400)

            story_id = UnfoldStudioService.get_story_id_from_play_instance_uuid(story_play_instance_uuid)
            target_knot_data = UnfoldStudioService.get_knot_data(story_id, target_knot_name)
            story_play_history = UnfoldStudioService.get_story_play_history(story_play_instance_uuid)

            backend = get_llm_backend()
            system_prompt, user_prompt = self.build_system_and_user_prompt(target_knot_data, story_play_history, user_input)
            if not backend.is_direction_cached(system_prompt, user_prompt, seed) and not request.user.is_authenticated:
                return JsonResponse({"error": "Authentication required for uncached AI generation."}, status=401)

            direction, content = self.get_next_direction_details_for_story(target_knot_data, story_play_history, user_input, seed)

            result = {
                "direction": direction,
                "content": content,
            }

            timeline = story_play_history.get("timeline", [])
            latest_timeline_entries = timeline[-5:]
            truncated_history = {"timeline": latest_timeline_entries}

            self.save_story_transition_record(story_play_instance_uuid, truncated_history, target_knot_data, user_input, result)
            
            return JsonResponse({"result": result}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
        except Exception as e:
            log.exception("Unexpected error in GetNextDirectionView")
            return JsonResponse({"error": str(e)}, status=500)

#@method_decorator(csrf_exempt, name="dispatch")
class AgentView(BaseView):

    def validate_request(self, request_body):
        required_fields = ['user_input', 'character_knot_name', 'target_knot_name', 'story_play_instance_uuid']
        for field in required_fields:
            if not request_body.get(field):
                return False, f"Missing required field: {field}"
        return True, None

    def generate_character_text(self, character_knot_data, target_knot_data, story_history, user_input, direction, seed):
        backend = TextGenerationFactory.create(settings.TEXT_GENERATION)

        character_voice = [ln.strip() for ln in character_knot_data.get("knotContents", []) if ln.strip()]
        voice_block = "\n".join(character_voice)

        target_knot = "\n".join(
            ln.strip() for ln in target_knot_data.get("knotContents", []) if ln.strip()
        )

        timeline = story_history.get("timeline", [])
        truncated_history = {"timeline": timeline[-10:]}

        user_prompt = AGENT_CHARACTER_USER_PROMPT_TEMPLATE % {
            "character_knot": voice_block,
            "target_knot": target_knot,
            "history": json.dumps(truncated_history, indent=2),
            "user_input": user_input,
            "direction": direction
        }

        try:
            return backend.get_ai_response_by_system_and_user_prompt(
                AGENT_CHARACTER_SYSTEM_PROMPT, user_prompt, seed, hit_cache=True
            )
        except Exception:
            log.exception("Error in generate_character_text")
            voice_lines = [ln.strip() for ln in character_knot_data.get("knotContents", []) if ln.strip()]
            voice_hint = voice_lines[0] if voice_lines else "…"
            return f"{voice_hint}\n\nWhat do you want?"

    def post(self, request):
        try:
            request_body = json.loads(request.body)
            seed = request_body.get('ai_seed') or settings.DEFAULT_AI_SEED

            story_play_instance_uuid = request_body.get("story_play_instance_uuid")
            character_knot_name = request_body.get("character_knot_name")
            target_knot_name = request_body.get("target_knot_name")
            user_input = request_body.get("user_input")
            log.debug("AgentView.post", character_knot_name=character_knot_name,
                      target_knot_name=target_knot_name,
                      story_play_instance_uuid=story_play_instance_uuid, seed=seed)

            validation_successful, failure_reason = self.validate_request(request_body)
            if not validation_successful:
                return JsonResponse({"error": failure_reason}, status=400)

            story_id = UnfoldStudioService.get_story_id_from_play_instance_uuid(story_play_instance_uuid)
            story_play_history = UnfoldStudioService.get_story_play_history(story_play_instance_uuid)

            character_knot_data = UnfoldStudioService.get_knot_data(story_id, character_knot_name)
            if not character_knot_data:
                return JsonResponse({"error": f"Character knot not found or empty: {character_knot_name}"}, status=404)

            target_knot_data = UnfoldStudioService.get_knot_data(story_id, target_knot_name)
            if not target_knot_data:
                return JsonResponse({"error": f"Target knot not found or empty: {target_knot_name}"}, status=404)

            # Call 1 — direction + bridge (target knot aware)
            direction_view = GetNextDirectionView()
            direction, content = direction_view.get_next_direction_details_for_story(
                target_knot_data=target_knot_data,
                story_history=story_play_history,
                user_input=user_input,
                seed=seed
            )

            if direction == StoryContinueDirections.DIRECT_CONTINUE:
                return JsonResponse({"result": {
                    "character_text": None,
                    "continue_decision": {
                        "direction": direction,
                        "content": content,
                    },
                }}, status=200)


            # Call 2 — character voice (target knot aware, steers without spoiling)
            character_text = self.generate_character_text(
                character_knot_data=character_knot_data,
                target_knot_data=target_knot_data,
                story_history=story_play_history,
                user_input=user_input,
                direction=direction,
                seed=seed
            )
            if direction in (StoryContinueDirections.NEEDS_INPUT, StoryContinueDirections.INVALID_USER_INPUT):
                # Character speaks AND ends with a question — shown as character_text, not guidance
                result = {
                    "character_text": character_text,
                    "continue_decision": {
                        "direction": direction,
                        "content": content,
                    },
                }

            elif direction == StoryContinueDirections.BRIDGE_AND_CONTINUE:
                if not content.get("bridge_text"):
                    log.warning("BRIDGE_AND_CONTINUE selected but bridge_text missing, falling back to NEEDS_INPUT")
                    direction = StoryContinueDirections.NEEDS_INPUT
                    content = {
                        "guidance_text": "What would you like to do next?",
                        "reason": "Bridge text missing from AI response"
                    }
                    result = {
                        "character_text": character_text,  # still show the character reply
                        "continue_decision": {
                            "direction": direction,
                            "content": content,
                        },
                    }   
                else:
                    result = {
                        "character_text": character_text,  # closing line, no question
                        "continue_decision": {
                            "direction": direction,
                            "content": content,
                        },
                    }
            else:
                # Fallback
                result = {
                    "character_text": character_text,
                    "continue_decision": {
                        "direction": direction,
                        "content": content,
                    },
                }
            return JsonResponse({"result": result}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
        except Exception as e:
            log.exception("Unexpected error in AgentView")
            return JsonResponse({"error": str(e)}, status=500)

    def get(self, request):
        return JsonResponse({"result": {"text": "agent endpoint: ok (GET)"}})
