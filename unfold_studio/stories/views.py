from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse, HttpResponseRedirect
from django.views import generic, View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.utils.timezone import now
from django.db.models import Q, F, Window
from django.db.models.functions import RowNumber
from django.core.paginator import Paginator
import reversion
from reversion.models import Version
import structlog

from stories.models import Story
from stories.forms import StoryForm, StoryVersionForm
from stories.mixins import StoryMixin
from books.models import Book
from literacy_events.models import LiteracyEvent
from comments.models import Comment
from comments.forms import CommentForm
from django.utils import timezone

log = structlog.get_logger("stories")


def u(request):
    "Helper to return username"
    return request.user.username if request.user.is_authenticated else "<anonymous>"


def new_story(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            story = Story(
                author=request.user,
                creation_date=now(),
                edit_date=now()
            )
        else:
            story = Story(
                author=None,
                creation_date=now(),
                edit_date=now(),
            )
        form = StoryForm(request.POST, instance=story)
        if form.is_valid():
            story = form.save()
            story.compile()
            story.update_priority()

            with reversion.create_revision():
                story.save()
                reversion.set_user(story.author)
                reversion.set_comment("Initial version of @story:{}".format(story.id))
            log.info(name="Application Alert", event="New Story Created", arg={"user": u(request), "story": story.id})
            return redirect('show_story', story.id)
    else:
        form = StoryForm()

    return render(request, 'unfold_studio/new_story.html', {'form': form})


def edit_story(request, story_id):
    story = Story.objects.get_editable_for_request_or_404(request, pk=story_id)
    story.edit_date = now()
    if request.method == "POST":
        form = StoryForm(request.POST, instance=story)
        if form.is_valid():
            story = form.save()
            with reversion.create_revision():
                story.save()
                reversion.set_user(story.author)
            return redirect('show_story', story.id)
    else:
        form = StoryForm(instance=story)
    return render(request, 'unfold_studio/edit_story.html', {'form': form, 'story': story})


def compile_story(request, story_id):
    "This is the route used to update story"
    story = Story.objects.get_editable_for_request_or_404(request, pk=story_id)
    story.edit_date = now()
    story.ink = request.POST['ink']
    story.compile()
    with reversion.create_revision():
        story.save()
        reversion.set_user(story.author)
        if not story.errors.exists():
            log.info(name="Application Alert", event="Story Editted", msg="OK", arg={"user": u(request), "story": story.id})
        else:
            log.warning(name="Application Alert", event="Story Editted", msg="Edit has Errors", arg={"user": u(request), "story": story.id})
    return JsonResponse(story.for_json())


def show_story(request, story_id):
    "Shows a story, using the same view regardless of whether it can be edited by the user"
    story = Story.objects.get_for_request_or_404(request, pk=story_id)
    editable = bool(story.author == request.user)
    addableBooks = request.user.books.exclude(stories=story) if request.user.is_authenticated else []
    response = render(request, 'unfold_studio/show_story.html', {
        'story': story,
        'editable': editable,
        'commentable': story.user_may_comment(request.user),
        'addableBooks': addableBooks}
    )
    response['Cache-Control'] = 'no-store'
    return response


def show_json(request, story_id):
    story = Story.objects.get_for_request_or_404(request, pk=story_id)
    return JsonResponse(story.for_json())


def embed_story(request, story_id):
    try:
        story = Story.objects.get(shared=True, pk=story_id)
    except Story.DoesNotExist:
        return render(request, 'unfold_studio/embed_error.html', {'reason': 'not_found'}, status=404)
    return render(request, 'unfold_studio/embed_story.html', {'story': story})


def compile_story_async(request, story_id):
    "Enqueues a Celery compilation task and returns the task_id for polling."
    from stories.tasks import compile_story_task
    story = Story.objects.get_editable_for_request_or_404(request, pk=story_id)
    story.ink = request.POST.get('ink', story.ink)
    story.save(update_fields=['ink'])
    task = compile_story_task.delay(story.id)
    return JsonResponse({'task_id': task.id})


def compile_story_status(request, story_id, task_id):
    "Polls the status of an async compilation task."
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    if result.ready():
        return JsonResponse({'status': 'done', 'result': result.get()})
    return JsonResponse({'status': result.state.lower()})


def show_ink(request, story_id):
    story = Story.objects.get_for_request_or_404(request, pk=story_id)
    return render(request, 'unfold_studio/show_ink.html', {'story': story})


class StoryVersionDetailView(View):
    verb = "viewed the history of"

    def get(self, request, *args, **kwargs):
        self.story = story = Story.objects.get_for_request_or_404(request, pk=kwargs['pk'])
        if not story.author:
            raise Http404()
        vIndex = int(kwargs['version'])  # 1-indexed!
        versions = Version.objects.get_for_object(story).exclude(revision__comment__exact='').reverse()
        if vIndex > versions.count() or vIndex < 1:
            raise Http404()
        comment = versions[vIndex - 1].revision.comment
        if len(comment) > 100:
            comment = comment[:100] + '...'
        return render(request, 'unfold_studio/show_story_version.html', {
            'story': versions[vIndex - 1].object,
            'comment': comment,
            'version': vIndex,
            'previousVersion': vIndex - 1 if vIndex > 1 else None,
            'nextVersion': vIndex + 1 if vIndex + 1 <= versions.count() else None
        })

    def get_object(self):
        return self.story


class StoryMethodView(LoginRequiredMixin, SingleObjectMixin, View):
    model = Story
    require_editable = True

    def get_queryset(self):
        if self.require_editable:
            return Story.objects.editable_for_request(self.request)
        else:
            return Story.objects.for_request(self.request)


class LoveStoryView(StoryMethodView):
    require_editable = False
    verb = "loved"

    def post(self, request, *args, **kwargs):
        story = self.get_object()
        if self.request.user.profile in story.loves.all():
            messages.warning(self.request, "You already love '{}'".format(story.title))
        elif self.request.user == story.author:
            messages.warning(self.request, "You can't love your own stories.".format(story.title))
        else:
            story.loves.add(self.request.user.profile)
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.LOVED_STORY,
                subject=self.request.user,
                story=story
            )
        return redirect('show_story', story.id)


class ForkStoryView(StoryMethodView):
    require_editable = False
    verb = "forked"

    def post(self, request, *args, **kwargs):
        parent = self.get_object()
        if not request.user.is_authenticated:
            messages.warning(request, "You must be logged in to fork stories")
            return redirect('show_story', parent.id)
        story = Story(
            author=request.user,
            parent=parent,
            title="{} (fork)".format(parent.title),
            ink=parent.ink,
            creation_date=now(),
            edit_date=now(),
        )
        with reversion.create_revision():
            story.save()
            reversion.set_user(story.author)
            if parent.author:
                reversion.set_comment("{} forked from @story:{} by @user:{}".format(story.title, parent.id,
                        parent.author.id))
            else:
                reversion.set_comment("{} forked from @story:{}".format(story.title, parent.id))
        story.compile()
        LiteracyEvent.objects.create(
            event_type=LiteracyEvent.FORKED_STORY,
            subject=request.user,
            story=story
        )
        return redirect('show_story', story.id)


class DeleteStoryView(StoryMethodView):
    verb = "deleted"

    def post(self, request, *args, **kwargs):
        story = self.get_object()
        if not request.user.is_authenticated:
            messages.warning(request, "You need to be logged in to delete stories")
            return redirect('show_story', story.id)
        if story.author != request.user:
            messages.warning(request, "You can only delete your own stories")
            return redirect('show_story', story.id)
        messages.success(request, "Deleted '{}'".format(story.title))
        for prompt in story.prompts_submitted.all():
            story.prompts_submitted.remove(prompt)
        for book in story.books.all():
            story.books.remove(book)
        story.deleted = True
        story.save()
        return redirect('show_user', request.user.username)


class ShareStoryView(StoryMethodView):
    verb = "shared"

    def post(self, request, *args, **kwargs):
        story = self.get_object()
        if story.author != request.user:
            messages.warning(request, "You can only share your own stories.")
        elif story.shared:
            messages.warning(request, "'{}' is already shared.".format(story.title))
        else:
            story.shared = True
            story.save()
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.PUBLISHED_STORY,
                subject=request.user,
                story=story
            )
        return redirect('show_story', story.id)


class UnshareStoryView(StoryMethodView):
    verb = "unshared"

    def post(self, request, *args, **kwargs):
        story = self.get_object()
        if story.author != request.user:
            messages.warning(request, "You can only unshare your own stories.")
        elif not story.shared:
            messages.warning(request, "'{}' is not shared.".format(story.title))
        else:
            story.shared = False
            story.save()
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.UNPUBLISHED_STORY,
                subject=request.user,
                story=story
            )
        return redirect('show_story', story.id)


class NewStoryVersionView(StoryMethodView):
    verb = "created a new version of"
    template = "unfold_studio/new_story_version.html"

    def get(self, request, *args, **kwargs):
        story = self.get_object()
        version = Version.objects.get_for_object(story).first()
        form = StoryVersionForm(initial={'comment': version.revision.comment})
        return render(request, self.template, {'form': form, 'story': story})

    def post(self, request, *args, **kwargs):
        form = StoryVersionForm(request.POST)
        story = self.get_object()
        if form.is_valid():
            version = Version.objects.get_for_object(story).first()
            revision = version.revision
            revision.comment = form.cleaned_data['comment']
            revision.save()
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.TAGGED_STORY_VERSION,
                subject=request.user,
                story=story
            )
            return redirect('show_story_versions', story.id)
        else:
            return render(request, self.template, {'form': form, 'story': story})


class StoryVersionListView(DetailView):
    model = Story
    template_name = "unfold_studio/story_version_list.html"
    context_object_name = 'story'

    def get_queryset(self):
        return Story.objects.for_request(self.request)

    def get(self, request, *args, **kwargs):
        story = self.get_object()
        if not story.author:
            raise Http404()
        if not story.user_may_comment(self.request.user):
            messages.warning(request, "You can only comment on a story if its author follows you or if they submit the story to one of your prompts.")
        if self.request.user == story.author:
            messages.success(request, "Tip: If you unfollow a user, their comments will disappear.")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        story = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid() and story.user_may_comment(request.user):
            comment = Comment.objects.create(
                author=request.user,
                story=story,
                message=form.cleaned_data['comment']
            )
            log.info("{} commented on {}".format(request.user, story))
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.COMMENTED_ON_STORY,
                subject=request.user,
                story=story
            )
            return redirect('show_story_versions', story.id)
        else:
            return redirect('show_story_versions', args=[story.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story = self.get_object()
        versions = Version.objects.get_for_object(story).exclude(revision__comment__exact='').reverse().annotate(
                index=Window(RowNumber()))

        comments = Comment.objects.for_story(story, self.request.user).all()

        def date(e):
            if isinstance(e, Comment):
                d = e.creation_date
            elif isinstance(e, Version):
                d = e.revision.date_created
            else:
                raise ValueError("Unexpected value: {}".format(e))
            if timezone.is_naive(d):
                d = timezone.make_aware(d)
            return d

        history = sorted(list(versions) + list(comments), key=date)
        context['history'] = [
            {
                'content': 'version' if isinstance(e, Version) else 'comment',
                'object': e
            }
            for e in history
        ]
        if story.user_may_comment(self.request.user):
            form = CommentForm()
            form.fields['comment'].label = "Add a comment"
            context['commentForm'] = form
        return context


class AddStoryToBookView(LoginRequiredMixin, View):
    """
    POST /stories/{story_id}/add_to_book/ with body {"book_id": N}
    Adds the story to the specified book owned by the current user.
    """

    def post(self, request, story_id, *args, **kwargs):
        import json as _json
        story = Story.objects.get_for_request_or_404(request, pk=story_id)
        try:
            body = _json.loads(request.body)
            book_id = body['book_id']
        except (ValueError, KeyError):
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest("book_id required")
        try:
            book = Book.objects.get(pk=book_id, owner=request.user)
        except Book.DoesNotExist:
            raise Http404
        if story in book.stories.all():
            messages.warning(request, "{} is already in {}".format(story.title, book.title))
        else:
            book.stories.add(story)
            messages.success(request, "You added {}".format(story.title))
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.ADDED_STORY_TO_BOOK,
                subject=request.user,
                story=story,
                book=book
            )
        return redirect('show_story', story.id)
