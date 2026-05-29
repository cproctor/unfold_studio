from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ValidationError
import re
from .models import Profile, DeprecatedUsername


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_story']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            from stories.models import Story
            self.fields['profile_story'].queryset = Story.objects.filter(author=user, shared=True)
            self.fields['profile_story'].required = False
            self.fields['profile_story'].empty_label = '(none)'


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[0-9a-zA-Z_]+$', username):
            raise ValidationError("Only letters, numbers, and _ are allowed in usernames")
        if not re.match(r'^[a-zA-Z][0-9a-zA-Z_]+$', username):
            raise ValidationError("Usernames must start with a letter")
        if DeprecatedUsername.objects.filter(old_username=username).exists():
            raise ValidationError("This username is not available.")
        return username

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise ValidationError("An account with this email already exists. Please sign up with a different address or click 'log in' above to reset your password.")
        return self.cleaned_data['email']

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


class StudentSignUpForm(UserCreationForm):
    def clean_username(self):
        if not re.match(r'^[0-9a-zA-Z_]+$', self.cleaned_data['username']):
            raise ValidationError("Only letters, numbers, and _ are allowed in usernames")
        if not re.match(r'^[a-zA-Z][0-9a-zA-Z_]+$', self.cleaned_data['username']):
            raise ValidationError("Usernames must start with a letter")
        return self.cleaned_data['username']

    class Meta:
        model = User
        fields = ('username',)

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
