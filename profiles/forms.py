from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ValidationError
import re


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    def clean_username(self):
        if not re.match(r'^[0-9a-zA-Z_]+$', self.cleaned_data['username']):
            raise ValidationError("Only letters, numbers, and _ are allowed in usernames")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )
