import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.conf import settings
from unfold_studio.models import Story
from django.utils.timezone import now
import reversion

@csrf_exempt
@require_http_methods(["POST"])
def compile_story(request):
    """
    An endpoint which tests whether ink code can compile successfully. For example: 
    % http POST http://local.unfoldstudio.net:8000/research/compile ink=@story.ink
    """
    try:
        ink = json.loads(request.body.decode('utf8'))['ink']
    except:
        return JsonResponse({"error": "request must contain JSON with key 'ink'"}, status_code=400)
    author, created = User.objects.get_or_create(username=settings.RESEARCH_USER)
    story = Story(
        title="Temporary", 
        description="Temporary", 
        author=author,
        ink=ink,
        creation_date=now(),
        edit_date=now(),
    )
    with reversion.create_revision():
        story.save()
        reversion.set_user(story.author)
        reversion.set_comment("Creating temporary story")
    story.compile()
    if story.errors.exists():
        response = {
            "compile_success": False,
            "errors": [err.message for err in story.errors.all()],
        }
    else:
        response = {
            "compile_success": True,
        }
    story.delete()
    return JsonResponse(response)

