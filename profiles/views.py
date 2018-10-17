from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views import View
from django.contrib.auth.models import User
from profiles.models import Profile, Event
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from unfold_studio.models import Story, Book
from django.conf import settings as s                                 
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger
from django.http import HttpResponse, Http404                         
import logging

log = logging.getLogger(__name__)    

def un(request):
    "Helper to return username"
    return request.user.username if request.user.is_authenticated else "<anonymous>"

class UserDetailView(DetailView):
    model = User
    slug_field = 'username'
    # Otherwise, we shadow the default 'user' available in templates
    # as the currently logged-in user
    context_object_name = 'profile_user'

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
            for e in self.request.user.events.filter(seen=False).all():
                e.seen = True
                e.save()
            context['stories'] = Story.objects.filter(author=self.object, deleted=False).all()
            context['feed'] = Event.objects.filter(
                Q(story__deleted=False) | Q(story__isnull=True),
                user=self.request.user
            )[:s.FEED_ITEMS_ON_PROFILE]
            context['feed_continues'] = Event.objects.filter(
                Q(story__deleted=False) | Q(story__isnull=True),
                user=self.request.user
            ).count() > s.FEED_ITEMS_ON_PROFILE
            context['Event'] = Event
        else:
            context['stories'] = Story.objects.filter(author=self.object, shared=True, deleted=False).all()
            
        log.info("{} viewed {}'s profile".format(un(self.request), self.object.username))
        return context

class FeedView(DetailView):
    model=User
    slug_field = 'username'
    template_name = "profiles/feed.html"
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user == self.object:
            raise Http404()
        for e in self.request.user.events.filter(seen=False).all():
            e.seen = True
            e.save()
        context['Event'] = Event
        events = Event.objects.filter(
            Q(story__deleted=False) | Q(story__isnull=True),
            user=self.request.user
        )
        paginator = Paginator(events, s.FEED_ITEMS_PER_PAGE)
        try:
            context['feed'] = paginator.page(self.request.GET.get('page'))
        except PageNotAnInteger:
            context['feed'] = paginator.page(1)
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
            log.info("{} followed {}".format(un(self.request), u.username))
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
            log.info("{} unfollowed {}".format(un(self.request), u.username))
        return redirect('show_user', u)
        








