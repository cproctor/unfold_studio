from django.forms import ModelForm, Form
from django import forms
from .models import Story
from django.core.exceptions import ValidationError

class StoryForm(ModelForm):
    class Meta:
        model = Story
        fields = [
            'title',
            'ink'
        ]

