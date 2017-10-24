from django.forms import ModelForm, Form
from django import forms
from .models import Story, Book
from django.core.exceptions import ValidationError

class StoryForm(ModelForm):
    class Meta:
        model = Story
        fields = ['title']

class SharedStoryBookForm(ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'stories']
    
