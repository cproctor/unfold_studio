from django.shortcuts import render, redirect                         
from django.http import HttpResponse, Http404                         
from django.conf import settings as s                                 
from django.shortcuts import render, get_object_or_404                
from django.views import generic                                      
from django.http import JsonResponse                                  
from django.contrib.auth import login
import json
import logging
import re
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

log = logging.getLogger('django')    


def story_queryset(request):
    "Returns a queryset for available stories in the current context"
    return Story.objects

def get_story(request, story_id, to_edit=False):
    try:
        if to_edit:
            return Story.objects.get(
                Q(public=True) | Q(author=request.user),
                id=story_id,
                sites__id=get_current_site(request).id,
                deleted=False
            )
        else:
            return Story.objects.get(
                Q(public=True) | Q(shared=True) | Q(author=request.user),
                id=story_id,
                sites__id=get_current_site(request).id,
                deleted=False
            )
    except Story.DoesNotExist:
        raise Http404()

def home(request):
    "The homepage shows a subset of stories with the highest priority."
    stories = Story.objects.filter(shared=True, deleted=False)[:s.FEATURED['STORIES_TO_SHOW']]
    return render(request, 'unfold_studio/home.html', {'stories': stories})

def browse(request):
    "Shows all stories, sorted by priority. Someday, I'll need to paginate this."
    stories = Story.objects.filter(
        Q(shared=True) | Q(public=True), 
        sites__id=get_current_site(request).id,
        deleted=False
    ).all()
    paginator = Paginator(stories, s.STORIES_PER_PAGE)
    page = request.GET.get('page')
    try:
        story_page = paginator.page(page)
    except PageNotAnInteger:
        story_page = paginator.page(1)
    
    return render(request, 'unfold_studio/list_stories.html', {'stories': story_page})

def new_story(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            story = Story(author=request.user, creation_date=now(), edit_date=now())
        else: 
            story = Story(
                author=None, 
                creation_date=now(), 
                edit_date=now(), 
                shared=True,
                public=True
            )
        form = StoryForm(request.POST, instance=story)
        if form.is_valid():
            story = form.save()
            story.compile_ink()
            with reversion.create_revision():
                story.save()
                reversion.set_user(story.author)
                reversion.set_comment("New story from fork")
            if not request.user.is_authenticated:
                #messages.success(request, "You're all set! This story is publicly editable. Sign up to write your own stories.")
                pass
            return redirect('show_story', story.id)
    else:
        form = StoryForm()

    return render(request, 'unfold_studio/new_story.html', {'form': form})

def edit_story(request, story_id):
    story = get_story(request, story_id)
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
    story = get_story(request, story_id, to_edit=True)
    story.edit_date = now()
    story.ink = request.POST['ink']
    story.compile_ink()
    with reversion.create_revision():
        story.save()
        reversion.set_user(story.author)
        if story.status == 'ok':
            reversion.set_comment("Story edited and compiled.")
        else:
            reversion.set_comment("Story edited and compiled (has error)")
    return JsonResponse(story.for_json())

def show_story(request, story_id):
    story = get_story(request, story_id)
    editable = int(story.author == request.user or story.public)
    return render(request, 'unfold_studio/show_story.html', {'story': story, 'editable': editable})

def show_json(request, story_id):
    story = get_story(request, story_id)
    return JsonResponse(story.for_json())

def show_ink(request, story_id):
    story = get_story(request, story_id)
    return render(request, 'unfold_studio/show_ink.html', {'story': story})

def about(request):
    story = get_story(request, s.ABOUT_STORY_ID)
    return render(request, 'unfold_studio/staticpage.html', {'story': story})

def for_teachers(request):
    story = get_story(request, s.TEACHERS_STORY_ID)
    return render(request, 'unfold_studio/staticpage.html', {'story': story})

def documentation(request):
    return render(request, 'unfold_studio/documentation.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = Profile(user=user)
            profile.save()
            login(request, user)
            messages.success(request, 
                "Welcome to Unfold Studio! Have fun, and please be a good community member.")
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

class StoryMethodView(LoginRequiredMixin, SingleObjectMixin, View):
    model = Story
    slug_field = 'id'

    def get_object(self, queryset=None):
        story = super().get_object(queryset)
        if story.deleted:
            raise Http404()
        return story

class LoveStoryView(StoryMethodView):
    def get(self, request, *args, **kwargs):
        story = self.get_object()
        if self.request.user.profile in story.loves.all():
            messages.warning(self.request, "You already love '{}'".format(story.title))
        elif self.request.user == story.author:
            messages.warning(self.request, "You can't love your own stories.".format(story.title))
        else:
            story.loves.add(self.request.user.profile)
            messages.success(self.request, "You loved '{}'".format(story.title))
        return redirect('show_story', story.id)
        
class ForkStoryView(StoryMethodView):
    def get(self, request, *args, **kwargs):
        parent = self.get_object()
        if not request.user.is_authenticated:
            messages.warning(request, "You must be logged in to fork stories")
            return redirect('show_story', parent.id)
        if parent.author == request.user:
            messages.warning(request, "You can't fork your own stories")
            return redirect('show_story', parent.id)
        story = Story(
            author=request.user, 
            parent=parent,
            title="{} (fork)".format(parent.title),
            ink=parent.ink,
            json=parent.json,
            status=parent.status,
            message=parent.message,
            err_line=parent.err_line,
            creation_date=now(), 
            edit_date=now(), 
        )
        story.save()
        #messages.success(self.request, "You have forked '{}'".format(story.title))
        return redirect('show_story', story.id)

class DeleteStoryView(StoryMethodView):
    def get(self, request, *args, **kwargs):
        story = self.get_object()
        if not request.user.is_authenticated:
            messages.warning(request, "You need to be logged in to delete stories")
            return redirect('show_story', parent.id) 
        if story.author != request.user:
            messages.warning(request, "You can only delete your own stories")
            return redirect('show_story', story.id)
        messages.success(request, "Deleted '{}'".format(story.title))
        story.deleted = True
        story.save()
        return redirect('home')
        
class ShareStoryView(StoryMethodView):
    def get(self, request, *args, **kwargs):
        story = self.get_object()
        if story.author != request.user:
            messages.warning(request, "You can only share your own stories.")
        elif story.shared:
            messages.warning(request, "'{}' is already shared.".format(story.title))
        else:
            story.shared = True
            story.save()
            messages.success(request, "You shared '{}'".format(story.title))
        return redirect('show_story', story.id)

class UnshareStoryView(StoryMethodView):
    def get(self, request, *args, **kwargs):
        story = self.get_object()
        if story.author != request.user:
            messages.warning(request, "You can only unshare your own stories.")
        elif not story.shared:
            messages.warning(request, "'{}' is not shared.".format(story.title))
        else:
            story.shared = False
            story.save()
            messages.success(request, "You shared '{}'".format(story.title))
        return redirect('show_story', story.id)

class CreateBookView(LoginRequiredMixin, CreateView):
    model = Book
    fields = ['title']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = "Create a new book"
        return context

    def post(self, request, *args, **kwargs):
        _book = Book(owner=request.user)
        form = self.get_form_class()(request.POST, instance=_book)
        if form.is_valid():
            book = form.save()
            return redirect('show_book', book.id)
        else:
            context = self.get_context_data(form=form)
            return render('book_form', context)

class BookListView(ListView):
    model = Book

class BookDetailView(DetailView):
    model = Book

class UpdateBookView(UpdateView):
    model = Book
    fields = ['title']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = "Edit {}".format(self.object.title)
        return context
    def get_success_url(self):
        return reverse('show_book', args=(self.object.id,))

def require_entry_point(request):
    return render(request, 'unfold_studio/require_entry_point.js', content_type="application/javascript")













