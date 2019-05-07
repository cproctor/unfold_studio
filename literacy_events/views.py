from django.shortcuts import render
from django.views.generic.edit import ProcessFormView
from literacy_events.models import LiteracyEvent
from literacy_events.forms import ReadingEventForm
from django.http import HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from unfold_studio.models import Story
import logging
log = logging.getLogger(__name__)    

class LogReadingEvent(ProcessFormView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            log.info("Ignoring anonymous logged reading")
            return HttpResponse("OK")
        form = ReadingEventForm(request.POST)
        if form.is_valid():
            story = Story.objects.get_for_request_or_404(request, pk=form.cleaned_data['story'])
            e = LiteracyEvent.objects.create(
                event_type=LiteracyEvent.STORY_READING,
                subject=request.user,
                story=story,
                extra=form.cleaned_data['path']
            )
            log.info(e)
            return HttpResponse("OK")
        else:
            raise Http404()
