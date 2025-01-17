import json
from django.views import View
from text_generation.backends import get_text_generation_backend
from django.conf import settings
from django.http import JsonResponse
from unfold_studio.commons.views import AuthenticatedView

class GenerateTextView(AuthenticatedView):

    def validate_request(self, request_body):
        prompt = request_body.get('prompt')
        if not prompt:
            return False, "prompt can not be empty"
        
        return True, None

    def post(self, request):
        try:
            request_body = json.loads(request.body)
            prompt = request_body.get('prompt')
            context_array = request_body.get('context_array')

            validation_successful, failure_reason = self.validate_request(request_body)
            if not validation_successful:
                return JsonResponse({"error": failure_reason}, status=400)

            backend = get_text_generation_backend(settings.TEXT_GENERATION)
            result = backend.generate(prompt, context_array)

            return JsonResponse({"result": result}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


