from django.forms import ModelForm, Form
from django import forms
from .models import Story, Book
from django.core.exceptions import ValidationError
from django.utils.http import urlencode

# TODO: Blurb should be here too.
class StoryForm(ModelForm):
    class Meta:
        model = Story
        fields = ['title']

class SharedStoryBookForm(ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'stories']

class SearchForm(Form):
    query = forms.CharField(max_length=100, label="Query")

    def querystring(self):
        "Returns the query formatted for the querystring"
        if self.is_valid():
            return urlencode(self.cleaned_data)
        else:
            return ""

class StoryVersionForm(Form):
    comment = forms.CharField(widget=forms.Textarea())
