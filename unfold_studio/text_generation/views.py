import json
from django.views import View
from text_generation.backends import get_text_generation_backend
from django.conf import settings
from django.http import JsonResponse
from unfold_studio.commons.views import AuthenticatedView
from .models import TextGenerationRecord
import hashlib

class GenerateTextView(AuthenticatedView):

    def validate_request(self, request_body):
        prompt = request_body.get('prompt')
        if not prompt:
            return False, "Prompt cannot be empty"
        return True, None

    def hash_prompt_and_context(self, prompt, context):
        combined = prompt + '|' + json.dumps(context, separators=(',', ':'))
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def get_cached_response(self, seed, hashed_key, backend_name):
        cache_entry = TextGenerationRecord.objects.filter(seed=seed, hashed_key=hashed_key, backend_name=backend_name)
        print(cache_entry)
        if cache_entry.exists():
            return cache_entry.first()
        else:
            return None

    def save_to_cache(self, seed, hashed_key, prompt, context, result, backend_name):
        TextGenerationRecord.objects.create(
            seed=seed,
            hashed_key=hashed_key,
            prompt=prompt,
            context=context,
            result=result,
            backend=backend_name,
        )

    def post(self, request):
        try:
            result={"ok":"ok"}
            request_body = json.loads(request.body)
            prompt = request_body.get('prompt')
            context_array = request_body.get('context_array', [])
            seed = request_body.get('seed', 42)
            print(seed)

            validation_successful, failure_reason = self.validate_request(request_body)
            if not validation_successful:
                return JsonResponse({"error": failure_reason}, status=400)

            hashed_key = self.hash_prompt_and_context(prompt, context_array)
            print(hashed_key)

            backend_config = settings.TEXT_GENERATION
            backend = get_text_generation_backend(backend_config)
            backend_name = backend.config['backend']
            print(backend_name)

            cached_result = self.get_cached_response(seed, hashed_key, backend_name)
            # if cached_result:
            #     return JsonResponse({"result": cached_result}, status=200)

            # result = backend.generate(prompt, context_array)

            # self.save_to_cache(seed, hashed_key, prompt, context_array, result, backend_name)

            return JsonResponse({"result": result}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
