from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import DetailView, ListView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef, Subquery
from prompts.models import Prompt, PromptStory
from prompts.forms import PromptSubmissionForm
from prompts.mixins import CSVResponseMixin
from unfold_studio.models import Story
from reversion.models import Version
import logging
from literacy_events.models import LiteracyEvent
from collections import defaultdict

log = logging.getLogger(__name__)    

def u(request):
    "Helper to return username"
    return request.user.username if request.user.is_authenticated else "<anonymous>"

class PromptsOwnedListView(ListView):
    model = Prompt
    context_object_name = 'prompts'
    template_name = 'prompts/list_prompts_owned.html'
    def get_queryset(self):
        return Prompt.objects.filter(owners=self.request.user)

class PromptsOwnedCSVView(CSVResponseMixin, View):

    def get_csv_filename(self):
        return timezone.now().strftime("unfold-studio-prompts-%Y-%m-%d.csv")

    def get(self, request, *args, **kwargs):
        users = User.objects.filter(groups__prompts_assigned__owners=request.user)
        prompts = request.user.prompts_owned.all()
        for p in prompts:
            annotations = { 
                "{} (assigned)".format(p): Exists(p.assignee_groups.filter(user=OuterRef('pk'))), 
                "{} (submission)".format(p): Subquery(p.submissions.filter(author=OuterRef('pk')).values('id')[:1])
            }
            users = users.annotate(**annotations)

        values = ['username', 'email', 'first_name', 'last_name']
        for p in prompts:
            values += ["{} (assigned)".format(p), "{} (submission)".format(p)]

        return self.render_to_csv(users.values(*values), dicts=True, fieldnames=values)

class PromptsAssignedListView(ListView):
    model = Prompt
    context_object_name = 'prompts'
    template_name = 'prompts/list_prompts_assigned.html'
    def get_queryset(self):
        return Prompt.objects.filter(assignee_groups__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prompts_with_submissions'] = [
            (p, p.submissions.filter(author=self.request.user).first())
            for p in self.get_queryset().all()
        ]
        return context

class PromptAssignedDetailView(DetailView):
    model = Prompt
    context_object_name = 'prompt'
    template_name = 'prompts/show_prompt_assigned.html'

    def get_queryset(self):
        return Prompt.objects.filter(assignee_groups__user=self.request.user)

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        form = PromptSubmissionForm()
        form.fields['story'].choices = [(s.id, s.title) for s in self.request.user.stories.all()]
        context['form'] = form
        context['submission'] = self.get_object().submissions.for_request(self.request).filter(author=self.request.user).first()
        return context

    def post(self, *args, **kwargs):
        form = PromptSubmissionForm(self.request.POST)
        form.fields['story'].choices = [(s.id, s.title) for s in self.request.user.stories.all()]
        if form.is_valid():
            story = Story.objects.get_editable_for_request_or_404(self.request, pk=form.cleaned_data['story'])
            version = Version.objects.get_for_object(story).last()
            PromptStory.objects.create(prompt=self.get_object(), story=story, 
                    submitted_story_version=version)
            log.info("{} submitted story {} to prompt {}".format(u(self.request), story, self.get_object()))
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.SUBMITTED_TO_PROMPT,
                subject=self.request.user,
                story=story,
                prompt=self.get_object()
            )
            return redirect('show_prompt_assigned', self.get_object().id)
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)

class ClearPromptSubmissionView(SingleObjectMixin, View):
    http_method_names = ['post']
    def post(self, *args, **kwargs):
        prompt = self.get_object()
        ps = PromptStory.objects.get(
            prompt=prompt, 
            story__author=self.request.user
        )
        story = ps.story
        ps.delete()
        log.info("{} cleared submitted story {} from prompt {}".format(u(self.request), story, self.get_object()))
        LiteracyEvent.objects.create(
            event_type=LiteracyEvent.UNSUBMITTED_FROM_PROMPT,
            subject=self.request.user,
            story=story,
            prompt=self.get_object()
        )
        return redirect('show_prompt_assigned', prompt.id)

    def get_queryset(self):
        return Prompt.objects.filter(assignee_groups__user=self.request.user)

class PromptOwnedDetailView(DetailView):
    model = Prompt
    context_object_name = 'prompt'
    template_name = 'prompts/show_prompt_owned.html'

    def get_queryset(self):
        return Prompt.objects.filter(owners=self.request.user)

    # TODO slow
    def get_context_data(self, **kwargs):
        prompt = self.get_object()
        context = super().get_context_data(**kwargs)
        submissions = self.get_object().submissions.for_request(self.request).distinct()
        submissionsByUsername = {s.author.username : s for s in submissions}
        gn = lambda groups: ", ".join(g.name for g in groups)
        submissionData = [
            (
                user, gn(user.groups.filter(id__in=prompt.assignee_groups.all()).all()), 
                submissionsByUsername.get(user.username)
            ) 
            for user in self.get_object().assignees.prefetch_related('groups').distinct()
        ]
        context['submissions'] = sorted(submissionData, key=lambda s: (s[1], s[0].username))
        return context
