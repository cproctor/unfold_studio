import json

from django.forms import ModelForm, Form
from django import forms
from stories.models import Story


class GenreTagField(forms.CharField):
    """Stores genres as a JSON array in a hidden input; free-text tag entry via JS widget."""

    widget = forms.HiddenInput

    def __init__(self, **kwargs):
        kwargs.setdefault('required', False)
        super().__init__(**kwargs)

    def to_python(self, value):
        if not value:
            return []
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(t).strip().lower() for t in parsed if str(t).strip()]
        except (json.JSONDecodeError, TypeError):
            pass
        return [t.strip().lower() for t in value.split(',') if t.strip()]

    def prepare_value(self, value):
        if isinstance(value, list):
            return json.dumps(value)
        if isinstance(value, str):
            return value  # already JSON from re-displayed form after validation error
        return '[]'


class StoryForm(ModelForm):
    genres = GenreTagField()

    class Meta:
        model = Story
        fields = ['title', 'description', 'genres']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['genres'] = self.instance.genres or []


class StoryVersionForm(Form):
    comment = forms.CharField(widget=forms.Textarea())
