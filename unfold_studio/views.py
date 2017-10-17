from django.shortcuts import render, redirect                         
from django.core.paginator import Paginator, EmptyPage                
from django.http import HttpResponse, Http404                         
from django.conf import settings as s                                 
from django.shortcuts import render, get_object_or_404                
from django.views import generic                                      
from django.http import JsonResponse                                  
from django.forms.models import model_to_dict                         
from django.contrib.auth.decorators import login_required             
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
import json
from django.core.serializers import serialize                         
from django.core.exceptions import ValidationError, PermissionDenied  
import logging
from datetime import datetime                                         
from random import choice
import re
from .forms import StoryForm
from .models import Story, Book
# TODO Do I need all this crap?

from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.http import HttpResponseRedirect

log = logging.getLogger('django')    

def home(request):
    stories = Story.objects.filter(featured=True).order_by('title').all()
    return render(request, 'unfold_studio/home.html', {'stories': stories})

def browse(request):
    stories = Story.objects.order_by('title').all()
    return render(request, 'unfold_studio/list_stories.html', {'stories': stories})

@login_required
def new_story(request):
    if request.method == "POST":
        story = Story(author=request.user, creation_date=datetime.now(), edit_date=datetime.now())
        form = StoryForm(request.POST, instance=story)
        if form.is_valid():
            story = form.save()
            story.compile_ink()
            story.save()
            if story.status == "ok":
                return redirect('show_story', story.id)
            else:
                return redirect('edit_story', story.id)
    else:
        form = StoryForm()

    return render(request, 'unfold_studio/new_story.html', {'form': form})

@login_required
def edit_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if request.method == "POST":
        form = StoryForm(request.POST, instance=story)
        if form.is_valid():
            story = form.save()
            story.compile_ink()
            story.save()
            log.info({
                "id": story.id,
                "status": story.status,
                "message": story.message,
                "ink": story.ink,
                "json": story.json,
                "title": story.title,
                "author": story.author,
                "timestamp": datetime.now()
            })
            if story.status == "ok":
                return redirect('show_story', story.id)
    else:
        form = StoryForm(instance=story)
    return render(request, 'unfold_studio/edit_story.html', {'form': form, 'story': story})
    
def show_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if story.status == 'ok':
        return render(request, 'unfold_studio/show_story.html', {'story': story})
    else:
        return render(request, 'unfold_studio/show_story_error.html', {'story': story})

def show_json(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if story.status == "ok":
        log.info(story.json)
        return JsonResponse(json.loads(story.json))
    else:
        return JsonResponse({
            "status": story.status,
            "message": story.message
        })

def show_ink(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    return render(request, 'unfold_studio/show_ink.html', {'story': story})

def delete_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    story.delete()
    return redirect('home')

def about(request):
    return render(request, 'unfold_studio/about.html')

def documentation(request):
    return render(request, 'unfold_studio/documentation.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})

class StoryMethodView(LoginRequiredMixin, SingleObjectMixin, View):
    model = Story
    slug_field = 'id'

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
        story = Story(author=request.user, parent=parent)
        # TODO How do we init a story without saving it? Hidden field on the form? Render new story view
        messages.success(self.request, "ONCE FORKS ARE IMPLEMENTED, you will have forked '{}'".format(story.title))
        return redirect('show_story', parent.id)

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
















