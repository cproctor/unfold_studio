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
from .models import Story
# TODO Do I need all this crap?

log = logging.getLogger('django')    

def home(request):
    stories = Story.objects.order_by('title').all()
    return render(request, 'unfold_studio/home.html', {'stories': stories})

def new_story(request):
    if request.method == "POST":
        form = StoryForm(request.POST)
        form.creation_date = datetime.now()
        form.edit_date = datetime.now()
        log.info(form)
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




