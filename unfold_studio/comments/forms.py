from django import forms
from comments.models import Comment

class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea())
