import json
import structlog
from text_generation.backends import get_llm_backend, TextGenerationFactory
from django.conf import settings
from django.http import JsonResponse
from commons.base.views import BaseView, AuthenticatedView
from .models import StoryTransitionRecord
from .services.unfold_studio import UnfoldStudioService
from .constants import (StoryContinueDirections, DIRECTION_DECISION_QUESTION, DIRECTION_DECISION_INPUT_TEMPLATE, NEXT_TURN_SYSTEM_PROMPT, NEXT_TURN_USER_PROMPT_TEMPLATE, AGENT_CHARACTER_SYSTEM_PROMPT, AGENT_CHARACTER_USER_PROMPT_TEMPLATE)
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

    def build_decision_input(self, target_knot_data, story_history, user_input):
        return DIRECTION_DECISION_INPUT_TEMPLATE % {
            'target_knot': target_knot_data.get('knotContents', []),
            'history': json.dumps(story_history, indent=2),
            'user_input': user_input
        }

    def build_next_turn_prompts(self, direction, target_knot_data, story_history, user_input):
        user_prompt = NEXT_TURN_USER_PROMPT_TEMPLATE % {
            'direction': direction,
            'target_knot': target_knot_data.get('knotContents', []),
            'history': json.dumps(story_history, indent=2),
            'user_input': user_input
        }
        return NEXT_TURN_SYSTEM_PROMPT, user_prompt

    def decide_direction(self, backend, target_knot_data, story_history, user_input, seed):
        """Uses the decisions model to pick the next direction. Returns (direction, decision)."""
        decision_input = self.build_decision_input(target_knot_data, story_history, user_input)
        decision = backend.get_choice_decision(
            decision_input, DIRECTION_DECISION_QUESTION, seed, hit_cache=True
        )
        direction = decision.get('choice')
        if direction not in StoryContinueDirections.values():
            raise ValueError(f"Invalid direction received: {direction}")
        return direction, decision

    def generate_next_turn_text(self, backend, direction, target_knot_data, story_history, user_input, seed):
        system_prompt, user_prompt = self.build_next_turn_prompts(
            direction, target_knot_data, story_history, user_input
        )
        text = backend.get_ai_response_by_system_and_user_prompt(
            system_prompt, user_prompt, seed, hit_cache=True
        )
        return (text or "").strip()

    def get_next_direction_details_for_story(self, target_knot_data, story_history, user_input, seed):
        default_direction = StoryContinueDirections.NEEDS_INPUT
        default_content = {
            "guidance_text": "What would you like to do next?",
            "reason": "System failure"
        }

        try:
            backend = get_llm_backend()

            direction, decision = self.decide_direction(
                backend, target_knot_data, story_history, user_input, seed
            )
            content = {
                "reason": f"Decision model chose {direction} (confidence: {decision.get('confidence')})"
            }

            if direction == StoryContinueDirections.BRIDGE_AND_CONTINUE:
                content["bridge_text"] = self.generate_next_turn_text(
                    backend, direction, target_knot_data, story_history, user_input, seed
                )
            elif direction == StoryContinueDirections.NEEDS_INPUT:
                content["guidance_text"] = self.generate_next_turn_text(
                    backend, direction, target_knot_data, story_history, user_input, seed
                )

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
            decision_input = self.build_decision_input(target_knot_data, story_play_history, user_input)
            if not backend.is_decision_cached(decision_input, [DIRECTION_DECISION_QUESTION], seed) and not request.user.is_authenticated:
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
