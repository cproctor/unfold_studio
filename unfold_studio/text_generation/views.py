import json
from django.views import View
from django.http import HttpResponse
from text_generation.backends import get_text_generation_backend
from django.conf import settings

class GenerateTextView(View):
    """Super-basic view! TODO:
        - require authentication
        - input and output error-checking
        - enable csrf checking (in urls.py)
    """
    def post(self, request):
        prompt = json.loads(request.body)['prompt']
        context_array = json.loads(request.body)['context_array']
        print(request.body)
        print(f"inside GenerateTextView context_array is: {context_array}")
        prompt += " ".join(context_array)
        print(f"inside GenerateTextView with final prompt: {prompt}")
        backend = get_text_generation_backend(settings.TEXT_GENERATION)
        result = backend.generate(prompt)
        data = {"result": result}
        return HttpResponse(json.dumps(data), content_type='application/json')
