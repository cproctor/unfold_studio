from django.forms import ModelForm, Form
from django import forms
from stories.models import Story

GENRE_CHOICES = [
    ('fantasy', 'Fantasy'),
    ('mystery', 'Mystery'),
    ('sci_fi', 'Science Fiction'),
    ('romance', 'Romance'),
    ('horror', 'Horror'),
    ('adventure', 'Adventure'),
    ('historical', 'Historical Fiction'),
    ('thriller', 'Thriller'),
    ('comedy', 'Comedy'),
    ('drama', 'Drama'),
]


class StoryForm(ModelForm):
    genres = forms.MultipleChoiceField(
        choices=GENRE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Story
        fields = ['title', 'description', 'genres']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['genres'] = self.instance.genres or []


class StoryVersionForm(Form):
    comment = forms.CharField(widget=forms.Textarea())
