from django import forms

class PromptSubmissionForm(forms.Form):
    story = forms.ChoiceField()

