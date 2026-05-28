from django.forms import ModelForm, Form
from django import forms
from stories.models import Story


class StoryForm(ModelForm):
    class Meta:
        model = Story
        fields = ['title', 'description']


class StoryVersionForm(Form):
    comment = forms.CharField(widget=forms.Textarea())
