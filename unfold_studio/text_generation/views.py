import json
from text_generation.backends import get_text_generation_backend
from django.conf import settings
from django.http import JsonResponse
from unfold_studio.commons.views import AuthenticatedView
from .models import TextGenerationRecord
import hashlib
from .services.unfold_studio import UnfoldStudioService

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
            backend = get_text_generation_backend(backend_config)
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


class GetNextActionView(AuthenticatedView):
    SYSTEM_PROMPT = """You are a story transition analyst. Analyze how user input leads to target story nodes:

    DIRECT_CONTINUE: Input directly matches target conditions chronologically
    BRIDGE_AND_CONTINUE: Requires narrative to connect input to target timeline
    NEEDS_INPUT: Needs clarification to maintain chronological consistency

    Consider temporal relationships: user input must precede target node events.
    Also the guidance_text/bridge_text you give should not include details of the target knot. 

    Example Flow:
    [Current Story] "You sit on your bed"
    [User Input] "drink coffee"
    [Target Node] "You wake up at 7AM tired"

    Good Bridge: 
    "After drinking coffee late at night, you struggle to sleep. The caffeine keeps you awake until..."

    Bad Bridge: 
    "You wake up tired and drink coffee" (wrong order)

        Follow this JSON format:
        {
            "probabilities": {
                "DIRECT_CONTINUE": 0.0-1.0,
                "BRIDGE_AND_CONTINUE": 0.0-1.0,
                "NEEDS_INPUT": 0.0-1.0
            },
            "direct_continue": {
                "reason": "...",
            },
            "bridge_and_continue": {
                "reason": "...",
                "bridge_text": "..." // Full narrative bridge text
            },
            "needs_input": {
                "reason": "...",
                "guidance_text": "...", // Question/prompt for next input from user
            }
        }

        Example:
        {
            "probabilities": {
                "DIRECT_CONTINUE": 0.3,
                "BRIDGE_AND_CONTINUE": 0.5,
                "NEEDS_INPUT": 0.2
            },
            "direct_continue": {
                "reason": "User specified exact target location",
            },
            "bridge_and_continue": {
                "reason": "Needs transition to hidden chamber",
                "bridge_text": "As you push the ancient door, it creaks open to reveal..."
            },
            "needs_input": {
                "reason": "Requires specific investigation focus",
                "guidance_text": "What part of the wall will you examine?",
            }
        }"""

    def validate_request(self, request_body):
        required_fields = ['user_input', 'target_knot_data', 'story_play_instance_uuid']
        for field in required_fields:
            if not request_body.get(field):
                return False, f"Missing required field: {field}"
        return True, None

    def get_direction_and_content_from_response(self, response):
        probabilities = response.get('probabilities', {})
        if not isinstance(probabilities, dict):
            raise ValueError("Invalid probabilities format")
            
        required_directions = ["DIRECT_CONTINUE", "BRIDGE_AND_CONTINUE", "NEEDS_INPUT"]
        for direction in required_directions:
            if direction not in probabilities:
                raise ValueError(f"Missing probability for {direction}")

        total_probability = int(sum(probabilities.values()))
        if total_probability != 1:
            raise ValueError(f"Total probability does not equal 1")

        max_prob = max(probabilities.values())
        selected_direction = next(
            direction for direction, prob in probabilities.items()
            if prob == max_prob
        )

        # CHANGE THE BELOW DIRECTION TO TEST DIFFERENT CASES
        # selected_direction = "DIRECT_CONTINUE"
        print(f"selected_direction: {selected_direction}")

        direction_content = response.get(selected_direction.lower(), {})
        
        if selected_direction == "BRIDGE_AND_CONTINUE":
            if "bridge_text" not in direction_content:
                raise ValueError("Missing bridge_text for BRIDGE_AND_CONTINUE")
                
        elif selected_direction == "NEEDS_INPUT":
            if "guidance_text" not in direction_content:
                raise ValueError("Missing guidance_text for NEEDS_INPUT")

        return selected_direction, direction_content



    def get_next_direction_for_story(self, target_knot_data, story_history, user_input):
        USER_PROMPT = f"""### Story Context ###
                        Target Knot: {target_knot_data.get('knotContents', [])}
                        History: {json.dumps(story_history, indent=2)}
                        User Input: {user_input}

                        ### Analysis Request ###
                        1. Probability distribution
                        2. Action parameters
                        3. Brief reasoning"""
        
        default_direction = "NEEDS_INPUT"
        default_content = {
            "guidance_text": "What would you like to do next?",
            "reason": "System failure"
        }

        try:
            backend_config = settings.TEXT_GENERATION
            backend = get_text_generation_backend(backend_config)
            response = backend.get_next_direction_for_story(self.SYSTEM_PROMPT, USER_PROMPT)
 
            if response.startswith("```json") and response.endswith("```"):
                response = response[7:-3].strip()
            response_json = json.loads(response)
            print(response_json)
            direction, content = self.get_direction_and_content_from_response(response_json)

            return direction, content
            
        except Exception as e:
            print("cacthing the exception")
            return default_direction, default_content


    def post(self, request):
        try: 
            request_body = json.loads(request.body)
            print(request_body)
            user_input = request_body.get('user_input')
            target_knot_data = request_body.get('target_knot_data')
            story_play_instance_uuid = request_body.get('story_play_instance_uuid')

            result = {}

            validation_successful, failure_reason = self.validate_request(request_body)
            if not validation_successful:
                return JsonResponse({"error": failure_reason}, status=400)

            story_play_history = UnfoldStudioService.get_story_play_history(story_play_instance_uuid)

            direction, content = self.get_next_direction_for_story(target_knot_data, story_play_history, user_input)
            print(f"Direction taken: {direction},  Content: {content}")

            result = {
                "direction": direction,
                "content": content,
            }
            
            return JsonResponse({"result": result}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)}, status=500)