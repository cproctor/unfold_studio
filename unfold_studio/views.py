from django.shortcuts import render, redirect                         
from django.http import HttpResponse, Http404                         
from django.conf import settings as s                                 
from django.shortcuts import render, get_object_or_404                
from django.views import generic                                      
from django.http import JsonResponse                                  
from django.contrib.auth import login
import json
import logging
from .forms import StoryForm
from .models import Story, Book
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
from profiles.forms import SignUpForm
from django.utils.timezone import now
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger
from unfold_studio.mixins import StoryMixin
from literacy_events.models import LiteracyEvent

log = logging.getLogger(__name__)    

def u(request):
    "Helper to return username"
    return request.user.username if request.user.is_authenticated else "<anonymous>"

def home(request):
    "The homepage shows a subset of stories with the highest priority."
    stories = Story.objects.for_request(request)[:s.STORIES_ON_HOMEPAGE]
    log.info("{} visited homepage".format(u(request)))
    return render(request, 'unfold_studio/home.html', {'stories': stories})

def browse(request):
    "Shows all stories, sorted by priority. Someday, I'll need to paginate this."
    stories = Story.objects.for_request(request).all()
    paginator = Paginator(stories, s.STORIES_PER_PAGE)
    page = request.GET.get('page')
    try:
        story_page = paginator.page(page)
    except PageNotAnInteger:
        story_page = paginator.page(1)
    
    log.info("{} browsed {}".format(u(request), story_page))
    messages.success(request, "Tip: Stories get sorted by how many loves and forks they get, and by their freshness.")
    return render(request, 'unfold_studio/list_stories.html', {'stories': story_page})

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
            story.sites.add(get_current_site(request))
            with reversion.create_revision():
                story.save()
                reversion.set_user(story.author)
                reversion.set_comment("New story")
            if not request.user.is_authenticated:
                messages.success(request, "You're all set! This story is publicly editable. Sign up to write your own stories.")
            log.info("{} created story {}".format(u(request), story.id))
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
                reversion.set_comment("Title changed to {}".format(story.title))
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
            log.info("{} edited story {} (ok)".format(u(request), story.id))
            reversion.set_comment("Story edited and compiled.")
        else:
            log.info("{} edited story {} (errors)".format(u(request), story.id))
            reversion.set_comment("Story edited and compiled (has error)")
    return JsonResponse(story.for_json())

def show_story(request, story_id):
    "Shows a story, using the same view regardless of whether it can be edited by the user"
    story = Story.objects.get_for_request_or_404(request, pk=story_id)
    editable = int(story.author == request.user or story.public)
    addableBooks = request.user.books.exclude(stories=story) if request.user.is_authenticated else []
    if story.author == request.user:
        log.info("{} viewed story {} (own story)".format(u(request), story.id))
    elif story.public:
        log.info("{} viewed story {} (public)".format(u(request), story.id))
    else:
        log.info("{} viewed story {} (owned by {})".format(u(request), story.id, story.author.username))
    return render(request, 'unfold_studio/show_story.html', {'story': story, 'editable': editable, 
            'addableBooks': addableBooks})

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
            log.info("{} signed up".format(u(request)))
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

class StoryMethodView(LoginRequiredMixin, SingleObjectMixin, View):
    model = Story
    slug_field = 'id'
    verb = "<undefined verb>"

    def get_queryset(self):
        return Story.objects.for_request(self.request)

    def log_action(self, request):
        story = self.get_object()
        if story.public:
            log.info("{} {} story {} (id {}; public)".format(u(request), self.verb, story.title, story.id))
        elif story.author == request.user:
            log.info("{} {} story {} (id {}; own story)".format(u(request), self.verb, story.title, story.id))
        else:
            log.info("{} {} story {} (id {}; by {})".format(u(request), self.verb, story.title, story.id, story.author.username))

class LoveStoryView(StoryMethodView):
    verb = "loved"
    def get(self, request, *args, **kwargs):
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
            self.log_action(request)
        return redirect('show_story', story.id)
        
class ForkStoryView(StoryMethodView):
    verb = "forked"
    def get(self, request, *args, **kwargs):
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
            reversion.set_comment("Story forked")
        story.compile()
        story.sites.add(get_current_site(self.request))
        #messages.success(self.request, "You have forked '{}'".format(story.title))
        self.log_action(request)
        LiteracyEvent.objects.create(
            event_type=LiteracyEvent.FORKED_STORY,
            subject=request.user,
            story=story
        )
        return redirect('show_story', story.id)

class DeleteStoryView(StoryMethodView):
    verb = "deleted"
    def get(self, request, *args, **kwargs):
        story = self.get_object()
        if not request.user.is_authenticated:
            messages.warning(request, "You need to be logged in to delete stories")
            return redirect('show_story', parent.id) 
        if story.author != request.user:
            messages.warning(request, "You can only delete your own stories")
            return redirect('show_story', story.id)
        messages.success(request, "Deleted '{}'".format(story.title))
        self.log_action(request)
        story.deleted = True
        story.save()
        return redirect('home')
        
class ShareStoryView(StoryMethodView):
    verb = "shared"
    def get(self, request, *args, **kwargs):
        story = self.get_object()
        if story.author != request.user:
            messages.warning(request, "You can only share your own stories.")
        elif story.shared:
            messages.warning(request, "'{}' is already shared.".format(story.title))
        else:
            story.shared = True
            story.save()
            self.log_action(request)
            #messages.success(request, "You shared '{}'".format(story.title))
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.PUBLISHED_STORY,
                subject=request.user,
                story=story
            )
        return redirect('show_story', story.id)

class UnshareStoryView(StoryMethodView):
    verb = "unshared"
    def get(self, request, *args, **kwargs):
        story = self.get_object()
        if story.author != request.user:
            messages.warning(request, "You can only unshare your own stories.")
        elif not story.shared:
            messages.warning(request, "'{}' is not shared.".format(story.title))
        else:
            story.shared = False
            story.save()
            self.log_action(request)
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.UNPUBLISHED_STORY,
                subject=request.user,
                story=story
            )
            #messages.success(request, "You unshared '{}'".format(story.title))
        return redirect('show_story', story.id)

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

    def get_queryset(self):
        return Book.objects.filter(sites__id=get_current_site(self.request).id)

class BookDetailView(DetailView):
    # TODO: Use this as a model for using Mixins. get_context_data is needlessly verbose.
    model = Book

    def get_queryset(self):
        return Book.objects.filter(sites__id=get_current_site(self.request).id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user if self.request.user.is_authenticated else None
        context['stories'] = self.get_object().stories.for_request(self.request)
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
    def get(self, request, *args, **kwargs):
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
    def get(self, request, *args, **kwargs):
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

def require_entry_point(request):
    return render(request, 'unfold_studio/require_entry_point.js', content_type="application/javascript")
