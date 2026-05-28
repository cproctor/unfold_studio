import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from stories.models import Story
from django.utils.timezone import now
import reversion

from research.decorators import require_api_key


@require_api_key
@require_http_methods(["POST"])
def compile_story(request):
    """
    An endpoint which tests whether ink code can compile successfully. For example:
    % http POST http://local.unfoldstudio.net:8000/research/compile ink=@story.ink \
          Authorization:"Bearer <key>"
    """
    try:
        ink = json.loads(request.body.decode('utf8'))['ink']
    except Exception:
        return JsonResponse({"error": "request must contain JSON with key 'ink'"}, status=400)
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
    response = {
        "compile_success": not story.errors.exists(),
        "errors": [err.message for err in story.errors.all()],
    }
    story.delete()
    return JsonResponse(response)


class ResearcherRequiredMixin:
    """Mixin requiring the user to be authenticated and have is_researcher=True."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not getattr(request.user.profile, 'is_researcher', False):
            messages.error(request, "Researcher access required.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class ResearcherAPIKeyView(ResearcherRequiredMixin, LoginRequiredMixin, View):
    """
    Shows the researcher's current API key and provides a rotate button.
    GET  → show key (or offer to create one)
    POST → rotate (revoke old, issue new) or create if none exists
    """
    template_name = 'research/api_key.html'

    def _get_or_create_key(self, user):
        from research.models import APIKey
        key = APIKey.objects.filter(owner=user, revoked=False).order_by('-created_at').first()
        if key is None:
            key = APIKey.objects.create(owner=user)
        return key

    def get(self, request, *args, **kwargs):
        from research.models import APIKey
        key = APIKey.objects.filter(owner=request.user, revoked=False).order_by('-created_at').first()
        return render(request, self.template_name, {'api_key': key})

    def post(self, request, *args, **kwargs):
        from research.models import APIKey
        # Revoke all existing active keys then create a new one
        APIKey.objects.filter(owner=request.user, revoked=False).update(revoked=True)
        new_key = APIKey.objects.create(owner=request.user)
        messages.success(request, "API key rotated. Copy your new key — it won't be shown again in full.")
        return render(request, self.template_name, {'api_key': new_key, 'just_rotated': True})
