from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views import View
from django.contrib.auth.models import User
from profiles.models import Profile, Event
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from unfold_studio.models import Story, Book

class UserDetailView(DetailView):
    model = User
    slug_field = 'username'

    def get_template_names(self):
        "Returns a special template if this is the user's own profile page"
        if self.request.user == self.object:
            return 'profiles/user_self_detail.html'
        else:
            return 'profiles/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.filter(owner=self.object).all()
        if self.request.user == self.object:
            context['stories'] = Story.objects.filter(author=self.object).all()
            context['feed'] = Event.objects.filter(user=self.request.user)[:10]
            context['Event'] = Event
        else:
            context['stories'] = Story.objects.filter(author=self.object, shared=True).all()
            
        return context

class FollowUserView(LoginRequiredMixin, SingleObjectMixin, View):
    model = User
    slug_field = 'username'

    def get(self, request, *args, **kwargs):
        u = self.get_object()
        if u.profile in self.request.user.profile.following.all():
            messages.warning(self.request, "You are already following {}".format(u.username))
        elif u == self.request.user:
            messages.warning(self.request, "Nice try. You can't follow yourself. :)")
        else:
            self.request.user.profile.following.add(u.profile)
            messages.success(self.request, "You are now following {}".format(u.username))
        return redirect('show_user', u)
        
class UnfollowUserView(LoginRequiredMixin, SingleObjectMixin, View):
    model = User
    slug_field = 'username'

    def get(self, request, *args, **kwargs):
        u = self.get_object()
        if u.profile not in self.request.user.profile.following.all():
            messages.warning(self.request, "You are not following {}".format(u.username))
        else:
            self.request.user.profile.following.remove(u.profile)
            messages.success(self.request, "You stopped following {}".format(u.username))
        return redirect('show_user', u)
        








