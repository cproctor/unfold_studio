from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ValidationError
import re


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=False, help_text='Inform a valid email address (Teachers/Regular users only).')
  
    #Dropdown choices
    USER_TYPE_CHOICES = [
    ('regular', 'Regular User'),
    ('student', 'Student'),
    ('teacher', 'Teacher/Instructor'),
    ]
    #Add dropdown
    user_type= forms.ChoiceField(
        choices= USER_TYPE_CHOICES,
        label= "I am a...",
        initial='regular',
        required= True
    )
    def clean_username(self):
        if not re.match(r'^[0-9a-zA-Z_]+$', self.cleaned_data['username']):
            raise ValidationError("Only letters, numbers, and _ are allowed in usernames")
        if not re.match(r'^[a-zA-Z][0-9a-zA-Z_]+$', self.cleaned_data['username']):
            raise ValidationError("Usernames must start with a letter")
        return self.cleaned_data['username']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_type = self.cleaned_data.get('user_type')

        # Logic: Email is required for Teachers and Regular Users
        if user_type in ['regular', 'teacher'] and not email:
            raise ValidationError("Email is required for this account type.")
        
        # Check uniqueness if email is provided
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        
        return email

    class Meta:
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            from .models import Profile
            # We create the profile, but is_teacher stays False regardless of the choice
            Profile.objects.create(user=user, is_teacher=False)
        return user
    
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
            from .models import Profile
            Profile.objects.create(user=user, is_teacher=False)
        return user
