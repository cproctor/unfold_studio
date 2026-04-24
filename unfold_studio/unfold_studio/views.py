from django.shortcuts import render, redirect                         
from django.http import HttpResponse, Http404                         
from django.conf import settings as s                                 
from django.shortcuts import render, get_object_or_404                
from django.views import generic                                      
from django.http import JsonResponse                                  
from django.contrib.auth import login
import json
import re
import structlog
from .forms import StoryForm, StoryVersionForm, BookForm, GENRE_CHOICES
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
from django.db.models import Q, F, Window
from django.db.models.functions import RowNumber
from django.db import OperationalError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from unfold_studio.mixins import StoryMixin
from unfold_studio.forms import SearchForm, GENRE_CHOICES
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from comments.models import Comment
from comments.forms import CommentForm
from django.utils import timezone
from datetime import timedelta

log = structlog.get_logger("unfold_studio")

BROWSE_STORIES_PER_PAGE = 10

def extract_compiled_story_preview(story):
    """
    Prefer readable prose from compiled Ink JSON in story.json.
    Fall back to story.description if needed.
    """
    desc = (story.description or "").strip()

    if not story.json:
        return desc

    try:
        compiled = json.loads(story.json)
    except Exception:
        return desc

    # Ink compiled story JSON marks narrative text with a leading caret (^).
    # Keep only those chunks to avoid runtime/control metadata.
    chunks = []

    def walk(node):
        if len(chunks) >= 12:
            return
        if isinstance(node, str):
            s = node.strip()
            if s.startswith("^"):
                s = s.lstrip("^").strip()
                s = re.sub(r"\s+", " ", s)
                if s:
                    chunks.append(s)
            return
        if isinstance(node, list):
            for item in node:
                walk(item)
                if len(chunks) >= 12:
                    return
            return
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
                if len(chunks) >= 12:
                    return

    start = compiled.get("root", compiled) if isinstance(compiled, dict) else compiled
    walk(start)

    preview = " ".join(chunks).strip()
    if preview:
        words = preview.split()
        return " ".join(words[:60]) + ("…" if len(words) > 60 else "")

    return desc


def browse_mode_badge_label(sort, has_search):
    if has_search:
        return ""
    if sort == "top":
        return "Top"
    if sort == "top_week":
        return "Top · week"
    if sort == "top_month":
        return "Top · month"
    if sort == "new":
        return "New"
    return ""


def u(request):
    "Helper to return username"
    return request.user.username if request.user.is_authenticated else "<anonymous>"

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

    story_list = list(stories[:s.STORIES_ON_HOMEPAGE])
    for st in story_list:
        st.hover_preview = extract_compiled_story_preview(st)
    return render(request, 'unfold_studio/home.html', {'stories': story_list})

def browse(request):
    "Shows all stories, sorted by priority. Someday, I'll need to paginate this."
    site = get_current_site(request)
    if request.user.is_authenticated:
        stories = Story.objects.for_site_user(site, request.user)
    else:
        stories = Story.objects.for_site_anonymous_user(site)

    genre_keys = {c[0] for c in GENRE_CHOICES}
    genre_param = (request.GET.get('genre') or '').strip()
    if genre_param and genre_param != 'all' and genre_param in genre_keys:
        stories = stories.filter(genres__contains=[genre_param])

    sort = (request.GET.get('sort') or 'all').strip()
    if sort not in ('all', 'top', 'top_week', 'top_month', 'new'):
        sort = 'all'

    query_text = (request.GET.get('query') or '').strip()
    has_query = bool(query_text)

    if has_query:
        form = SearchForm({'query': query_text})
        if not form.is_valid():
            messages.warning(request, "Please enter a valid search query")
            return redirect('list_stories')

        q = form.cleaned_data['query'].strip()
        query = SearchQuery(q)
        stories = stories.annotate(
            rank=SearchRank(F('search'), query),
        ).filter(
            Q(rank__gte=s.SEARCH_RANK_CUTOFF) |
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(author__username__icontains=q)
        ).order_by('-rank', '-priority', '-id')
    else:
        form = SearchForm()
        now_ts = timezone.now()
        if sort == 'all':
            stories = stories.order_by('-priority', '-id')
        elif sort == 'new':
            stories = stories.order_by('-edit_date', '-id')
        elif sort == 'top_week':
            week_ago = now_ts - timedelta(days=7)
            stories = stories.filter(edit_date__gte=week_ago).order_by('-priority', '-id')
        elif sort == 'top_month':
            month_ago = now_ts - timedelta(days=30)
            stories = stories.filter(edit_date__gte=month_ago).order_by('-priority', '-id')
        elif sort == 'top':
            stories = stories.order_by('-priority', '-id')
        else:
            stories = stories.order_by('-priority', '-id')

    if request.user.is_authenticated:
        stories = stories.select_related('author').prefetch_related('loves')

    def browse_qs(removals=(), **updates):
        q = request.GET.copy()
        q.pop('page', None)
        for key in removals:
            q.pop(key, None)
        for key, val in updates.items():
            q[key] = val
        return q.urlencode()

    genre_links = [{'slug': 'all', 'label': 'All', 'qs': browse_qs(removals=('genre',))}]
    for slug, label in GENRE_CHOICES:
        genre_links.append({'slug': slug, 'label': label, 'qs': browse_qs(genre=slug)})

    preserve = request.GET.copy()
    preserve.pop('page', None)
    browse_querystring = preserve.urlencode()

    paginator = Paginator(stories, BROWSE_STORIES_PER_PAGE)
    page = request.GET.get('page', 1)
    try:
        try:
            story_page = paginator.page(page)
        except PageNotAnInteger:
            story_page = paginator.page(1)
        except EmptyPage:
            story_page = paginator.page(paginator.num_pages)

        has_search = bool(has_query and form.is_valid())
        browse_mode_badge = browse_mode_badge_label(sort, has_search)
        for st in story_page:
            st.hover_preview = extract_compiled_story_preview(st)

        return render(request, 'unfold_studio/list_stories.html', {
            'stories': story_page,
            'form': form,
            'search_value': query_text,
            'browse_querystring': browse_querystring,
            'genre_links': genre_links,
            'current_sort': sort,
            'current_genre': genre_param or 'all',
            'has_search_query': has_search,
            'browse_mode_badge': browse_mode_badge,
            'qs_sort_all': browse_qs(sort='all'),
            'qs_sort_top': browse_qs(sort='top'),
            'qs_sort_top_week': browse_qs(sort='top_week'),
            'qs_sort_top_month': browse_qs(sort='top_month'),
            'qs_sort_new': browse_qs(sort='new'),
            'qs_refine_all': browse_qs(removals=('genre', 'sort')),
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
                public=True
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
    editable = int(story.author == request.user or story.public)
    addableBooks = request.user.books.exclude(stories=story) if request.user.is_authenticated else []
    return render(request, 'unfold_studio/show_story.html', {
        'story': story, 
        'editable': editable, 
        'commentable': story.user_may_comment(request.user),
        'addableBooks': addableBooks}
    )

def show_json(request, story_id):
    story = Story.objects.get_for_request_or_404(request, pk=story_id)
    return JsonResponse(story.for_json())

def show_ink(request, story_id):
    story = Story.objects.get_for_request_or_404(request, pk=story_id)
    return render(request, 'unfold_studio/show_ink.html', {'story': story})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 
                "Welcome to Unfold Studio! Have fun, and please be a good community member.")
            log.info(name="Application Alert", event="New User Sign Up", arg={"user": u(request)})
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

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
        story.sites.add(get_current_site(self.request))
        #messages.success(self.request, "You have forked '{}'".format(story.title))
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
    form_class = BookForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = "Create a new book"
        return context

    def post(self, request, *args, **kwargs):
        _book = Book(owner=request.user)
        form = BookForm(request.POST, instance=_book)
        if form.is_valid():
            book = form.save(commit=False)
            book.genres = form.cleaned_data.get('genres', [])
            book.save()
            book.sites.add(get_current_site(request))
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.PUBLISHED_BOOK,
                subject=request.user,
                book=book
            )
            return redirect('show_book', book.id)
        else:
            context = self.get_context_data(form=form)
            return render(request, 'unfold_studio/book_form.html', context)

class BookListView(ListView):
    model = Book
    template_name = 'unfold_studio/books_list.html'

    def get_queryset(self):
        site = get_current_site(self.request)
        qs = Book.objects.filter(sites__id=site.id).select_related('owner').prefetch_related('stories')
        query = self.request.GET.get('query', '').strip()
        if query:
            qs = qs.filter(
                Q(title__icontains=query) | Q(owner__username__icontains=query) | Q(description__icontains=query)
            )
        return qs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genre_filter = self.request.GET.get('genre', '')
        query = self.request.GET.get('query', '').strip()
        all_books = list(context['object_list'])

        # If searching, filter by genre if one is active, then show flat results
        if query:
            if genre_filter == 'other':
                search_results = [b for b in all_books if not b.genres]
            elif genre_filter:
                search_results = [b for b in all_books if genre_filter in (b.genres or [])]
            else:
                search_results = all_books

            context['genre_groups'] = {}
            context['ungenred_books'] = []
            context['search_results'] = search_results
            context['genre_choices'] = GENRE_CHOICES
            context['active_genre'] = genre_filter
            context['query'] = query
            context['is_search'] = True
            return context

        # Genre filtering
        if genre_filter == 'other':
            all_books = [b for b in all_books if not b.genres]
        elif genre_filter:
            all_books = [b for b in all_books if genre_filter in (b.genres or [])]

        # Group books by genre for display
        genre_label_map = dict(GENRE_CHOICES)
        genre_groups = {}
        ungenred = []
        for book in all_books:
            if book.genres:
                for g in book.genres:
                    if genre_filter and genre_filter != 'other' and g != genre_filter:
                        continue
                    label = genre_label_map.get(g, g.title())
                    genre_groups.setdefault(label, []).append(book)
            else:
                ungenred.append(book)

        context['genre_groups'] = genre_groups
        context['ungenred_books'] = ungenred
        context['search_results'] = []
        context['genre_choices'] = GENRE_CHOICES
        context['active_genre'] = genre_filter
        context['query'] = query
        context['is_search'] = False
        return context
 

class BookDetailView(DetailView):
    # TODO: Use this as a model for using Mixins. get_context_data is needlessly verbose.
    model = Book
    template_name = 'unfold_studio/book_detail.html'

    def get_queryset(self):
        return Book.objects.filter(sites__id=get_current_site(self.request).id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stories = self.get_object().stories.for_request(self.request).select_related('author').prefetch_related('loves')
        
        stories_with_snippets = []
        for story in stories:
            snippet = self._extract_snippet(story)
            stories_with_snippets.append((story, snippet))
        
        context['stories'] = stories
        context['stories_with_snippets'] = stories_with_snippets
        return context
    
    def _extract_snippet(self, story):
        import json, re
        desc = (story.description or "").strip()
        if not story.json:
            return desc
        try:
            compiled = json.loads(story.json)
        except Exception:
            return desc
        chunks = []
        def walk(node):
            if len(chunks) >= 12:
                return
            if isinstance(node, str):
                s = node.strip()
                if s.startswith("^"):
                    s = s.lstrip("^").strip()
                    s = re.sub(r"\s+", " ", s)
                    if s:
                        chunks.append(s)
                return
            if isinstance(node, list):
                for item in node:
                    walk(item)
                    if len(chunks) >= 12:
                        return
            if isinstance(node, dict):
                for v in node.values():
                    walk(v)
                    if len(chunks) >= 12:
                        return
        start = compiled.get("root", compiled) if isinstance(compiled, dict) else compiled
        walk(start)
        preview = " ".join(chunks).strip()
        if preview:
            words = preview.split()
            return " ".join(words[:60]) + ("…" if len(words) > 60 else "")
        return desc

class UpdateBookView(UpdateView):
    model = Book
    form_class = BookForm

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
