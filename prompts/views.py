from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView, FormView
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef, Subquery
from prompts.models import Prompt, PromptStory
from prompts.forms import PromptSubmissionForm
from prompts.mixins import CSVResponseMixin
from unfold_studio.models import Story, Book
from reversion.models import Version
import logging
from literacy_events.models import LiteracyEvent
from literacy_groups.models import LiteracyGroup
from literacy_groups.mixins import LiteracyGroupContextMixin
from collections import defaultdict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

log = logging.getLogger(__name__)    

def u(request):
    "Helper to return username"
    return request.user.username if request.user.is_authenticated else "<anonymous>"

class ShowPromptView(LiteracyGroupContextMixin, DetailView):
    model = Prompt
    context_object_name = 'prompt'

    def get_queryset(self):
        return self.group.prompts.filter(deleted=False)

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        form = PromptSubmissionForm()
        form.fields['story'].choices = [(s.id, s.title) for s in self.request.user.stories.all()]
        context['form'] = form
        context['group'] = self.group
        context['submission'] = self.get_object().submissions.filter(author=self.request.user).first()
        if self.user_is_leader:
            context = self.get_context_data_for_leader(context)
        return context

    def get_context_data_for_leader(self, context):
        submissions = self.object.submissions.prefetch_related('author').all()
        submissions_by_member = {s.author : s for s in submissions}
        context['member_submissions'] = [
            (m, submissions_by_member.get(m), self.has_new_material(submissions_by_member.get(m)))
            for m in self.group.members.all()
        ]
        return context

    # TODO slow. Should be done with a subquery.
    def has_new_material(self, story):
        """
        Returns a boolean indicating whether or not the story has something new the prompt owner may
        want to respond to.
        """
        if story is None: 
            return False
        if not story.comments.filter(author__in=self.group.leaders.all()).exists():
            return True
        latestTeacherComment = story.comments.filter(author__in=self.group.leaders.all()).order_by(
                '-creation_date').first()
        return (
            story.comments.filter(
                author=story.author, 
                creation_date__gt=latestTeacherComment.creation_date
            ).exists() or 
            Version.objects.get_for_object(story).filter(
                revision__date_created__gt=latestTeacherComment.creation_date
            ).exclude(
                revision__comment__exact=''
            ).exists()
        )
            
    def get_template_names(self):
        if self.user_is_leader:
            return ["prompts/show_prompt_as_leader.html"]
        else:
            return ["prompts/show_prompt.html"]

    def post(self, *args, **kwargs):
        "Handle submission to a prompt"
        form = PromptSubmissionForm(self.request.POST)
        form.fields['story'].choices = [(s.id, s.title) for s in self.request.user.stories.all()]
        if form.is_valid():
            prompt = self.get_object()
            story = Story.objects.get_editable_for_request_or_404(self.request, pk=form.cleaned_data['story'])
            version = Version.objects.get_for_object(story).last()
            PromptStory.objects.create(prompt=self.get_object(), story=story, 
                    submitted_story_version=version)
            log.info("{} submitted story {} to prompt {}".format(u(self.request), story, self.get_object()))
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.SUBMITTED_TO_PROMPT,
                subject=self.request.user,
                story=story,
                prompt=self.get_object(),
                literacy_group=self.get_object().literacy_group,
            )
            if prompt.book:
                prompt.book.stories.add(story)
            return redirect('show_prompt', self.group.id, self.get_object().id)
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)

class CreatePromptView(LiteracyGroupContextMixin, CreateView):
    model = Prompt
    url_group_key = "pk"
    fields = ['name', 'description', 'due_date']

    def post(self, request, *args, **kwargs):
        prompt = Prompt(
            author = self.request.user,
            literacy_group=self.group,
            creation_date=timezone.now()
        )
        form = self.get_form_class()(request.POST, instance=prompt)
        if form.is_valid():
            prompt = form.save()
            log.info("{} created prompt {} (id: {})".format(request.user, prompt.name, prompt.id))
            return redirect('show_prompt', self.group.id, prompt.id)
        else:
            context = self.get_context_data(form=form)
            return render('prompts/prompt_form.html', context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Create new prompt"
        context['group'] = self.group
        return context


class UpdatePromptView(LiteracyGroupContextMixin, UpdateView):
    model = Prompt
    fields = ['name', 'description', 'due_date']

    def get_queryset(self):
        return self.group.prompts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edit prompt"
        context['group'] = self.group
        return context

    def get_success_url(self):
        return reverse('show_prompt', args=(self.group.id, self.get_object().id))

class DeletePromptView(LiteracyGroupContextMixin, SingleObjectMixin, View):
    require_leader = True

    def post(self, request, *args, **kwargs):
        prompt = self.get_object()
        prompt.deleted = True
        prompt.save()
        messages.success(request, "Deleted {}".format(prompt.name))
        return redirect('show_group', self.group.id)

    def get_queryset(self):
        return self.group.prompts.filter(deleted=False)

class ExportPromptAsCsvView(LiteracyGroupContextMixin, CSVResponseMixin, DetailView):
    queryset = Prompt.objects

    def get_csv_filename(self):
        return timezone.now().strftime("unfold-studio-group-{}-prompt-{}-%Y-%m-%d.csv".format(
                self.group.id, self.get_object().id))

    def get(self, request, *args, **kwargs):
        submissions_by_user = {s.author: s for s in self.get_object().submissions.all()}
        member_submissions = [(m, submissions_by_user.get(m)) for m in self.group.members.all()]
        values = [(m.username, s.title if s else None, s.id if s else None, reverse('show_story', args=(s.id,)) if s else None) for m, s in member_submissions]
        fields = ['username', 'story_title', 'story_id', 'story_url']
        log.info("{} downloaded prompt {} (group {}) as CSV".format(request.user, self.get_object().id, self.group.id))
        return self.render_to_csv(values, fieldnames=fields)

class ClearPromptSubmissionView(LiteracyGroupContextMixin, SingleObjectMixin, View):
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
            prompt=self.get_object(),
            literacy_group=self.get_object().literacy_group,
        )
        if prompt.book:
            prompt.book.stories.remove(story)
        return redirect('show_prompt', self.group.id, prompt.id)

    def get_queryset(self):
        return self.group.prompts

class PublishAsBookView(LiteracyGroupContextMixin, SingleObjectMixin, View):
    http_method_names = ['post']
    require_leader = True

    def post(self, request, *args, **kwargs):
        prompt = self.get_object()
        if prompt.book:
            messages.warning(request, "{} is already published as a book".format(prompt.name))
            log.warning("{} tried to re-publish {} as a book".format(request.user), prompt.name)
            return redirect('show_prompt', prompt.id)
        book_desc = "This automatically-generated book contains stories submitted to @prompt:{}".format(prompt.id)
        book = Book.objects.create(
            owner=request.user, 
            title="Submissions to {}".format(prompt.name),
            description=book_desc
        )
        book.sites.add(prompt.literacy_group.site)
        prompt.book = book
        prompt.save()
        for story in prompt.submissions.all():
            book.stories.add(story)
        log.info("{} published {} as a book".format(request.user, prompt.name))
        LiteracyEvent.objects.create(
            event_type=LiteracyEvent.PUBLISHED_PROMPT_AS_BOOK,
            subject=self.request.user,
            prompt=prompt,
            book=book,
            literacy_group=prompt.literacy_group,
        )
        return redirect('show_book', book.id)
    
    def get_queryset(self):
        return self.group.prompts.filter(deleted=False)

class UnpublishBookView(LiteracyGroupContextMixin, SingleObjectMixin, View):
    http_method_names = ['post']
    require_leader = True

    def post(self, request, *args, **kwargs):
        prompt = self.get_object()
        if not prompt.book:
            messages.warning(request, "{} is not published as a book".format(prompt.name))
            log.warning("{} tried to unpublish {} when it was not published".format(request.user, prompt.name))
            return redirect('show_prompt', self.group.id, prompt.id)
        prompt.book.deleted = True
        prompt.book.save()
        prompt.book = None
        prompt.save()
        log.info("{} unpublished {} as a book".format(request.user, prompt.name))
        LiteracyEvent.objects.create(
            event_type=LiteracyEvent.UNPUBLISHED_PROMPT_AS_BOOK,
            subject=self.request.user,
            prompt=prompt,
            literacy_group=prompt.literacy_group,
        )
        return redirect('show_prompt', self.group.id, prompt.id)
            
    def get_queryset(self):
        return self.group.prompts.filter(deleted=False)

