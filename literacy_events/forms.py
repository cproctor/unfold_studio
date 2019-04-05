from django import forms
from literacy_events.models import LiteracyEvent

class ReadingEventForm(forms.Form):
    story = forms.IntegerField()
    path = forms.CharField()
