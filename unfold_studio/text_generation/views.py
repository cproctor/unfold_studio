import json
from text_generation.backends import TextGenerationFactory
from django.conf import settings
from django.http import JsonResponse
from commons.base.views import AuthenticatedView
from .models import TextGenerationRecord, StoryTransitionRecord
import hashlib
from .services.unfold_studio import UnfoldStudioService
from .constants import (StoryContinueDirections, CONTINUE_STORY_SYSTEM_PROMPT, CONTINUE_STORY_USER_PROMPT_TEMPLATE)

class GenerateTextView(AuthenticatedView):

    def validate_request(self, request_body):
        prompt = request_body.get('prompt')
        if not prompt:
            return False, "Prompt cannot be empty"
        return True, None

    def get_prompt_and_context_hash(self, prompt, context):
        combined = prompt + '|' + json.dumps(context, separators=(',', ':'))
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def get_text_generation_backend_config_hash(self, config):
        config_str = json.dumps(config, separators=(',', ':'), sort_keys=True)
        return hashlib.sha256(config_str.encode('utf-8')).hexdigest()


    def get_cached_response(self, seed, hashed_key, backend_config_hash):
        cache_entry = TextGenerationRecord.objects.filter(seed=seed, hashed_key=hashed_key, backend_config_hash=backend_config_hash)
        if cache_entry.exists():
            return cache_entry.first().result
        else:
            return None

    def save_to_cache(self, seed, hashed_key, prompt, context, result, backend_config, backend_config_hash):
        TextGenerationRecord.objects.create(
            seed=seed,
            hashed_key=hashed_key,
            prompt=prompt,
            context=context,
            result=result,
            backend_config=backend_config,
            backend_config_hash=backend_config_hash,
        )

    def post(self, request):
        try: 
            request_body = json.loads(request.body)
            prompt = request_body.get('prompt')
            context_array = request_body.get('context_array', [])
            seed = request_body.get('ai_seed') or settings.DEFAULT_AI_SEED

            validation_successful, failure_reason = self.validate_request(request_body)
            if not validation_successful:
                return JsonResponse({"error": failure_reason}, status=400)

            hashed_key = self.get_prompt_and_context_hash(prompt, context_array)

            backend_config = settings.TEXT_GENERATION
            backend = TextGenerationFactory.create(backend_config)
            backend_config_hash = self.get_text_generation_backend_config_hash(backend_config)

            cached_result = self.get_cached_response(seed, hashed_key, backend_config_hash)
            if cached_result:
                return JsonResponse({"result": cached_result}, status=200)

            result = backend.generate(prompt, context_array)
            self.save_to_cache(seed, hashed_key, prompt, context_array, result, backend_config, backend_config_hash)

            return JsonResponse({"result": result}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class GetNextDirectionView(AuthenticatedView):


    def validate_request(self, request_body):
        required_fields = ['user_input', 'target_knot_data', 'story_play_instance_uuid']
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
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error in data: {str(e)}")
            raise
        except ValueError as e:
            print(f"Data validation failed: {str(e)}")
            raise
        except Exception:
            print(f"Unexpected error occured in parsing data: {str(e)}")
            raise

    def determine_next_direction_details_from_ai_response(self, data):
        probabilities = data.get('probabilities', {})
        max_prob = max(probabilities.values())
        selected_direction = next(
            direction for direction, prob in probabilities.items()
            if prob == max_prob
        )

        # SET THE BELOW DIRECTION TO TEST DIFFERENT CASES
        # selected_direction = "NEEDS_INPUT"
        # selected_direction = "DIRECT_CONTINUE"
        # selected_direction = "BRIDGE_AND_CONTINUE"
        if selected_direction not in StoryContinueDirections.values():
            raise ValueError("Invalid direction received")

        selected_direction_content = data.get(selected_direction.lower(), {})

        return selected_direction, selected_direction_content


    def get_next_direction_details_for_story(self, target_knot_data, story_history, user_input):
        default_direction = StoryContinueDirections.NEEDS_INPUT
        default_content = {
            "guidance_text": "What would you like to do next?",
            "reason": "System failure"
        }

        try:
            backend_config = settings.TEXT_GENERATION
            backend = TextGenerationFactory.create(backend_config)

            system_prompt, user_prompt = self.build_system_and_user_prompt(target_knot_data, story_history, user_input)
            response = backend.get_ai_response_by_system_and_user_prompt(system_prompt, user_prompt)
            print(response)

            parsed_response = self.parse_and_validate_ai_response(response)
            direction, content = self.determine_next_direction_details_from_ai_response(parsed_response)

            return direction, content
            
        except Exception as e:
            print(f"Exception occoured in get_next_direction_details_for_story: {str(e)}")
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
            user_input = request_body.get('user_input')
            target_knot_data = request_body.get('target_knot_data')
            story_play_instance_uuid = request_body.get('story_play_instance_uuid')

            result = {}

            validation_successful, failure_reason = self.validate_request(request_body)
            if not validation_successful:
                return JsonResponse({"error": failure_reason}, status=400)

            story_play_history = UnfoldStudioService.get_story_play_history(story_play_instance_uuid)

            direction, content = self.get_next_direction_details_for_story(target_knot_data, story_play_history, user_input)

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
            print(str(e))
            return JsonResponse({"error": str(e)}, status=500)