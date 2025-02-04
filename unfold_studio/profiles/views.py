from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views import View
from django.contrib.auth.models import User
from profiles.models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from unfold_studio.models import Story, Book
from prompts.models import Prompt
from django.conf import settings as s                                 
from django.db.models import Q, OuterRef, Subquery
from django.core.paginator import Paginator, PageNotAnInteger
from django.http import HttpResponse, Http404                         
from django.contrib.sites.shortcuts import get_current_site
import structlog

from literacy_events.models import Notification, LiteracyEvent

log = structlog.get_logger("unfold_studio")  
  

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
        context['books'] = Book.objects.for_request(self.request).filter(owner=self.object).all()
        context['stories'] = Story.objects.for_request(self.request).filter(author=self.object).all()
        if not self.object.is_active:
            raise Http404()
        if self.request.user == self.object:
            Notification.objects.mark_all_seen_for_user(self.request.user)
            notifications_raw = Notification.objects.for_request(self.request).prefetch_related(
                "event__subject", 
                "event__story__author",
                "event__book",
                "event__literacy_group"
                )
            notifications = [
                {
                    "notification": notification,
                    "event": notification.event,
                    "subject": notification.event.subject,
                    "object_user": notification.event.object_user,
                    "story": notification.event.story,
                    "book": notification.event.book,
                    "literacy_group": notification.event.literacy_group,
                    "story_visible": notification.story_visible
                }
                for notification in notifications_raw
            ]
            context['username'] = self.request.user.username
            context['feed'] = notifications[:s.FEED_ITEMS_ON_PROFILE]
            context['feed_continues'] = (notifications_raw.count() > s.FEED_ITEMS_ON_PROFILE)
            context['LiteracyEvent'] = LiteracyEvent
            context['prompts_to_submit'] = Prompt.objects.unsubmitted_for_user(
                self.request.user
            ).select_related('literacy_group')
        else:
            if self.request.user.is_authenticated and (self.object not in self.request.user.profile.following.all()):
                messages.success(self.request, "Tip: If you follow a user, you'll see when they publish new stories.")
        log.info(name="Profile Alert", event="Profile Viewed", 
                 args={"request": un(self.request), "profile_username": self.object.username})
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
        Notification.objects.mark_all_seen_for_user(self.request.user)
        context['LiteracyEvent'] = LiteracyEvent
        notifications_raw = Notification.objects.for_request(self.request).prefetch_related(
                "event__subject", 
                "event__story__author",
                "event__book",
                "event__literacy_group"
                )
        notifications = [
                {
                    "notification": notification,
                    "event": notification.event,
                    "subject": notification.event.subject,
                    "object_user": notification.event.object_user,
                    "story": notification.event.story,
                    "book": notification.event.book,
                    "literacy_group": notification.event.literacy_group,
                    "story_visible": notification.story_visible
                }
                for notification in notifications_raw
            ]
        
        paginator = Paginator(notifications, s.FEED_ITEMS_PER_PAGE)
        context['username'] = self.request.user.username
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
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.FOLLOWED,
                subject=self.request.user,
                object_user=u
            )
            log.info(name="Profile Alert", event = "Follow Request", 
                     args={"follower": un(self.request), "following": u.username})
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
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.UNFOLLOWED,
                subject=self.request.user,
                object_user=u
            )
            log.info(name="Profile Alert", event="Unfollow Request", 
                     args={"follower": un(self.request), "following": u.username})
        return redirect('show_user', u)
        
