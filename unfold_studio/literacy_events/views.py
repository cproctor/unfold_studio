from django.shortcuts import render
from django.views.generic.edit import ProcessFormView
from literacy_events.models import LiteracyEvent
from literacy_events.forms import ReadingEventForm
from django.http import HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from unfold_studio.models import Story
import structlog
log = structlog.get_logger("unfold_studio")    

class LogReadingEvent(ProcessFormView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            log.info(name="Literacy Events Alert", event="Anonymous Reading Event")
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
            log.info(name="Literacy Event Alert", event="New Literacy Event Created", args={"literacy_event"})
            return HttpResponse("OK")
        else:
            raise Http404()
