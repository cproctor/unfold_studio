from django.forms import Form
from django import forms
from django.utils.http import urlencode


class SearchForm(Form):
    query = forms.CharField(max_length=100, label="Query")

    def querystring(self):
        "Returns the query formatted for the querystring"
        if self.is_valid():
            return urlencode(self.cleaned_data)
        else:
            return ""
