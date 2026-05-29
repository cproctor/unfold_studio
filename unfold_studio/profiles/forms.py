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
    email = forms.EmailField(max_length=254, required=False, help_text='Inform a valid email address (Teachers/Regular users only).')

    USER_TYPE_CHOICES = [
        ('regular', 'Regular User'),
        ('student', 'Student'),
        ('teacher', 'Teacher/Instructor'),
    ]

    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        label="I am a...",
        initial='regular',
        required=True
    )

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
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        user_type = cleaned_data.get('user_type')

        if user_type in ['regular', 'teacher'] and not email:
            self.add_error('email', 'Email is required for this account type.')

        return cleaned_data

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
