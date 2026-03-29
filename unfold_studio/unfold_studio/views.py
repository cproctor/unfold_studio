from django.shortcuts import render, redirect                         
from django.http import HttpResponse, Http404                         
from django.conf import settings as s                                 
from django.shortcuts import render, get_object_or_404                
from django.views import generic                                      
from django.http import JsonResponse                                  
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
import json
import structlog
from .forms import StoryForm, StoryVersionForm
from .models import Story, Book, StoryPlayInstance, StoryPlayRecord
from profiles.models import Profile
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
import reversion
from reversion.models import Version
from profiles.forms import SignUpForm
from django.utils.timezone import now
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q, F, Window, Value, FloatField
from django.db.models.functions import RowNumber, Coalesce
from django.db import OperationalError
from django.core.paginator import Paginator, PageNotAnInteger
from unfold_studio.mixins import StoryMixin
from unfold_studio.forms import SearchForm
from literacy_events.models import LiteracyEvent
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from comments.models import Comment
from comments.forms import CommentForm
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from unfold_studio.anonymous_session import (
    add_anonymous_owned_story,
    get_anonymous_owned_story_ids,
    owns_anonymous_story,
    remove_anonymous_owned_story,
)

log = structlog.get_logger("unfold_studio")    

def u(request):
    "Helper to return username"
    return request.user.username if request.user.is_authenticated else "<anonymous>"

def anonymous_welcome(request):
    return render(request, 'anonymous_mode_entry.html')


def home(request):
    "The homepage shows a subset of stories with the highest priority."
    site = get_current_site(request)
    if request.user.is_authenticated:
        for g in request.user.groups.filter(id__in=s.GROUP_HOMEPAGE_MESSAGES.keys()).all():
            messages.warning(request, s.GROUP_HOMEPAGE_MESSAGES[g.id])
        stories = Story.objects.for_site_user(site, request.user)
        stories = stories.select_related('author').prefetch_related('loves')
    else:
        site = get_current_site(request)
        stories = Story.objects.for_site_anonymous_user(site)

    stories = stories[:s.STORIES_ON_HOMEPAGE]
    return render(request, 'unfold_studio/home.html', {'stories': stories})

def browse(request):
    "Shows all stories, sorted by priority. Someday, I'll need to paginate this."
    site = get_current_site(request)
    if request.user.is_authenticated:
        stories = Story.objects.for_site_user(site, request.user)
    else:
        stories = Story.objects.for_site_anonymous_user(site)

    if request.GET.get('query'):
        form = SearchForm(request.GET)
        if form.is_valid():
            raw_q = (form.cleaned_data.get('query') or '').strip()
            if not raw_q:
                messages.warning(request, "Please enter a valid search query")
                return redirect('list_stories')
            # websearch: friendlier multi-word matching than plainto_tsquery.
            query = SearchQuery(raw_q, search_type='websearch')
            # Substring fallback: FTS misses many title/ink cases; also match each word (len>=3).
            text_q = Q(title__icontains=raw_q) | Q(ink__icontains=raw_q)
            for w in raw_q.split():
                w = w.strip('.,!?\"\'()[]')
                if len(w) >= 3:
                    text_q |= Q(title__icontains=w) | Q(ink__icontains=w)
            stories = stories.annotate(
                rank=SearchRank(F('search'), query),
                score=Coalesce(
                    F('rank') * F('priority') / (F('rank') + F('priority')),
                    Value(0.0),
                    output_field=FloatField(),
                ),
            ).filter(
                Q(rank__gte=s.SEARCH_RANK_CUTOFF)
                | Q(author__username__icontains=raw_q)
                | text_q
            ).exclude(
                author__isnull=True, public=False, shared=False
            ).order_by('-score', '-priority')
        else:
            messages.warning(request, "Please enter a valid search query")
            return redirect('list_stories')
    else:
        form = SearchForm()

    if request.user.is_authenticated:
        stories = stories.select_related('author').prefetch_related('loves')

    paginator = Paginator(stories, s.STORIES_PER_PAGE)
    page = request.GET.get('page', 1)
    try:
        story_page = paginator.page(page)
        return render(request, 'unfold_studio/list_stories.html', {
            'stories': story_page, 
            'form': form
        })
    except OperationalError:
        messages.warning(request, "Search is not supported using the current database.")
        return redirect('list_stories')

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
                public=False,
                shared=False,
            )
        form = StoryForm(request.POST, instance=story)
        if form.is_valid():
            story = form.save()
            story.compile()
            story.update_priority()
            story.sites.add(get_current_site(request))
            with reversion.create_revision():
                story.save()
                reversion.set_user(story.author)
                reversion.set_comment("Initial version of @story:{}".format(story.id))
            log.info(name="Application Alert", event="New Story Created", arg={"user": u(request), "story": story.id})
            if not request.user.is_authenticated:
                add_anonymous_owned_story(request, story.id)
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
    "This is the route used to update story "
    story = Story.objects.get_editable_for_request_or_404(request, pk=story_id)
    story.edit_date = now()
    story.ink = request.POST['ink']
    story.compile()
    # Share/Unshare can commit between our get() and save(); refresh visibility flags so
    # we do not clobber shared/public with stale values (lost-update race with beforeunload save).
    story.refresh_from_db(fields=["shared", "public"])
    with reversion.create_revision():
        story.save()
        reversion.set_user(story.author)
        if not story.errors.exists():
            log.info(name="Application Alert", event="Story Editted", msg="OK", arg={"user": u(request), "story": story.id})
        else:
            log.warning(name="Application Alert", event="Story Editted", msg="Edit has Errors", arg={"user": u(request), "story": story.id})
    return JsonResponse(story.for_json())

def _user_may_edit_story(request, story):
    if request.user.is_authenticated:
        return story.author_id == request.user.id or bool(story.public)
    return owns_anonymous_story(request, story)


def show_story(request, story_id):
    "Shows a story, using the same view regardless of whether it can be edited by the user"
    story = Story.objects.get_for_request_or_404(request, pk=story_id)
    may_edit = _user_may_edit_story(request, story)
    editable = int(may_edit)
    addableBooks = request.user.books.exclude(stories=story) if request.user.is_authenticated else []
    ai_enabled = request.user.is_authenticated
    draft_local_backup = (not request.user.is_authenticated) and may_edit
    return render(request, 'unfold_studio/show_story.html', {
        'story': story,
        'editable': editable,
        'owns_anonymous_story': owns_anonymous_story(request, story),
        'commentable': story.user_may_comment(request.user),
        'addableBooks': addableBooks,
        'ai_enabled': ai_enabled,
        'draft_local_backup': draft_local_backup,
        'can_fork_anonymously': (
            not request.user.is_authenticated and (story.public or story.shared)
        ),
    })

def show_json(request, story_id):
    story = Story.objects.get_for_request_or_404(request, pk=story_id)
    return JsonResponse(story.for_json())

def show_ink(request, story_id):
    story = Story.objects.get_for_request_or_404(request, pk=story_id)
    return render(request, 'unfold_studio/show_ink.html', {'story': story})

class ClaimAwareLoginView(LoginView):
    """
    After username/password login, attach an anonymous session-owned story to the user
    when claim_story is present (same rules as signup).
    """

    template_name = "registration/login.html"

    def get(self, request, *args, **kwargs):
        raw = request.GET.get("claim_story")
        if raw is not None and str(raw).strip().isdigit():
            request.session["pending_claim_story"] = int(str(raw).strip())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        raw = self.request.GET.get("claim_story")
        if raw is not None and str(raw).strip().isdigit():
            ctx["claim_story_id"] = int(str(raw).strip())
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        claim_id = None
        raw = self.request.POST.get("claim_story")
        if raw is not None and str(raw).strip().isdigit():
            claim_id = int(str(raw).strip())
        if claim_id is None:
            claim_id = self.request.session.pop("pending_claim_story", None)
        if claim_id is None:
            return response
        if claim_id not in get_anonymous_owned_story_ids(self.request):
            return response
        story = Story.objects.filter(pk=claim_id, author__isnull=True).first()
        if not story:
            return response
        story.author = self.request.user
        story.save()
        remove_anonymous_owned_story(self.request, claim_id)
        return redirect("show_story", claim_id)


def signup(request):
    claim_story_raw = request.POST.get('claim_story') if request.method == 'POST' else request.GET.get('claim_story')
    claim_story_id = None
    if claim_story_raw is not None and str(claim_story_raw).strip().isdigit():
        claim_story_id = int(str(claim_story_raw).strip())

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request,
                "Welcome to Unfold Studio! Have fun, and please be a good community member.")
            log.info(name="Application Alert", event="New User Sign Up", arg={"user": u(request)})

            if claim_story_id is not None and claim_story_id in get_anonymous_owned_story_ids(request):
                story = Story.objects.filter(
                    pk=claim_story_id,
                    author__isnull=True,
                ).first()
                if story:
                    story.author = user
                    story.save()
                    remove_anonymous_owned_story(request, claim_story_id)
                    return redirect('show_story', claim_story_id)

            next_url = request.POST.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return HttpResponseRedirect(next_url)

            return redirect('home')
    else:
        form = SignUpForm()

    raw_next = request.POST.get('next') if request.method == 'POST' else request.GET.get('next')
    raw_next = raw_next or ''
    next_url = ''
    if raw_next and url_has_allowed_host_and_scheme(
        raw_next,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = raw_next

    return render(request, 'registration/signup.html', {
        'form': form,
        'claim_story_id': claim_story_id,
        'next_url': next_url,
    })

class StoryVersionDetailView(View):
    verb = "viewed the history of"

    def get(self, request, *args, **kwargs):
        self.story = story = Story.objects.get_for_request_or_404(request, pk=kwargs['pk'])
        if not story.author:
            raise Http404()
        vIndex = int(kwargs['version']) # 1-indexed!
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
        
class ForkStoryView(SingleObjectMixin, View):
    model = Story

    def get_queryset(self):
        return Story.objects.for_request(self.request)

    def post(self, request, *args, **kwargs):
        parent = self.get_object()
        site = get_current_site(request)
        if request.user.is_authenticated:
            story = Story(
                author=request.user,
                parent=parent,
                title="{} (fork)".format(parent.title),
                description=parent.description,
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
            story.sites.add(site)
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.FORKED_STORY,
                subject=request.user,
                story=story
            )
            return redirect('show_story', story.id)

        if not (parent.public or parent.shared):
            messages.warning(request, "You can only fork public or shared stories.")
            return redirect('show_story', parent.id)

        story = Story(
            author=None,
            parent=parent,
            title="{} (fork)".format(parent.title),
            description=parent.description,
            ink=parent.ink,
            creation_date=now(),
            edit_date=now(),
            public=False,
            shared=False,
        )
        with reversion.create_revision():
            story.save()
            reversion.set_user(None)
            reversion.set_comment("{} forked from @story:{}".format(story.title, parent.id))
        story.compile()
        story.sites.add(site)
        add_anonymous_owned_story(request, story.id)
        return redirect('show_story', story.id)

class DeleteStoryView(StoryMethodView):
    verb = "deleted"
    def post(self, request, *args, **kwargs):
        story = self.get_object()
        if not request.user.is_authenticated:
            messages.warning(request, "You need to be logged in to delete stories")
            return redirect('show_story', parent.id) 
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
            #messages.success(request, "You shared '{}'".format(story.title))
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
            #messages.success(request, "You unshared '{}'".format(story.title))
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
                author = request.user,
                story = story,
                message = form.cleaned_data['comment']
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

        comments = Comment.objects.for_story(story).all()

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

class CreateBookView(LoginRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = "Create a new book"
        return context

    def post(self, request, *args, **kwargs):
        _book = Book(owner=request.user)
        form = self.get_form_class()(request.POST, instance=_book)
        if form.is_valid():
            book = form.save()
            book.sites.add(get_current_site(request))
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.PUBLISHED_BOOK,
                subject=request.user,
                book=book
            )
            log.info("{} created book {} (id {})".format(request.user, book.title, book.id))
            return redirect('show_book', book.id)
        else:
            context = self.get_context_data(form=form)
            return render('book_form', context)

class BookListView(ListView):
    model = Book
    paginate_by = 12
    def get_queryset(self):
        return Book.objects.filter(sites__id=get_current_site(self.request).id).select_related('owner')

class BookDetailView(DetailView):
    # TODO: Use this as a model for using Mixins. get_context_data is needlessly verbose.
    model = Book

    def get_queryset(self):
        return Book.objects.filter(sites__id=get_current_site(self.request).id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user if self.request.user.is_authenticated else None
        context['stories'] = self.get_object().stories.for_request(self.request).select_related('author').prefetch_related('loves')
        return context

class UpdateBookView(UpdateView):
    model = Book
    fields = ['title', 'description']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Book.objects.for_request(self.request).filter(owner=self.request.user)
        else:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = "Edit {}".format(self.object.title)
        return context

    def get_success_url(self):
        return reverse('show_book', args=(self.object.id,))

class AddStoryToBookView(LoginRequiredMixin, StoryMixin, DetailView):
    def post(self, request, *args, **kwargs):
        book = self.get_object(Book.objects.filter(owner=request.user))
        story = self.get_story()    # Lookup defaults to using story_id URL kwarg
        if story in book.stories.all():
            messages.warning(self.request, "{} is already in {}".format(story.title, book.title))
            log.warning("{} tried to re-add {} ({}) to book {} ({})".format(
                    u(request), story.title, story.id, book.title, book.id))
        else:
            book.stories.add(story)
            messages.success(self.request, "You added {}".format(story.title))
            log.info("{} added {} ({}) to book {} ({})".format(
                    u(request), story.title, story.id, book.title, book.id))
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.ADDED_STORY_TO_BOOK,
                subject=request.user,
                story=story,
                book=book
            )
        return redirect('show_book', book.id)
            
class RemoveStoryFromBookView(LoginRequiredMixin, StoryMixin, DetailView):
    def post(self, request, *args, **kwargs):
        book = self.get_object(Book.objects.filter(owner=request.user))
        story = self.get_story(queryset=book.stories.all())    # Lookup defaults to using story_id URL kwarg
        book.stories.remove(story)
        messages.success(self.request, "You removed {}".format(story.title))
        log.info("{} removed {} ({}) from book {} ({})".format(
                u(request), story.title, story.id, book.title, book.id))
        LiteracyEvent.objects.create(
            event_type=LiteracyEvent.REMOVED_STORY_FROM_BOOK,
            subject=request.user,
            story=story,
            book=book
        )
        return redirect('show_book', book.id)

class CreateStoryPlayInstanceView(CreateView):

    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        user_id = user.id if user else None
        request_body = json.loads(request.body)

        story_id = request_body['story_id']

        story_play_instance = StoryPlayInstance.objects.create(
            user_id=user_id,
            story_id=story_id
        )

        return JsonResponse({"story_play_instance_uuid": str(story_play_instance.uuid)})


class CreateStoryPlayRecordView(CreateView):

    def post(self, request, *args, **kwargs):
        request_body = json.loads(request.body)

        story_play_instance_uuid = request_body['story_play_instance_uuid']
        data_type = request_body['data_type']
        data = request_body['data']
        story_point = request_body['story_point']

        story_play_instance = StoryPlayInstance.objects.get(uuid=story_play_instance_uuid)

        story_play_record = StoryPlayRecord.objects.create(
            story_play_instance=story_play_instance,
            data_type=data_type,
            data=data,
            story_point=story_point,
        )

        return JsonResponse({"story_play_record_uuid": str(story_play_record.uuid)})

def require_entry_point(request):
    return render(request, 'unfold_studio/require_entry_point.js', content_type="application/javascript")

def embed_entry_point(request):
    return render(request, 'unfold_studio/embed_entry_point.js', content_type="application/javascript")
