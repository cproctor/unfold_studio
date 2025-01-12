from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.sites.shortcuts import get_current_site
from literacy_groups.models import LiteracyGroup
from literacy_groups.forms import LiteracyGroupForm
from literacy_events.models import LiteracyEvent
from django.db.models import Count
from django.views.generic.base import View
from django.db.models import Q
import structlog
from django.contrib import messages
from literacy_groups.mixins import LiteracyGroupContextMixin

log = structlog.get_logger("unfold_studio")    

# Create your views here.
class ListGroupsView(LoginRequiredMixin, ListView):
    model = LiteracyGroup
    context_object_name = 'groups'
    template_name = 'literacy_groups/list_groups.html'

    def get_queryset(self):
        qs = self.request.user.literacy_groups.filter(site=get_current_site(self.request))
        qs = qs.order_by('name')
        return qs

class CreateGroupView(LoginRequiredMixin, CreateView):
    model = LiteracyGroup
    fields = ['name', 'anyone_can_join']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Create new group"
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.profile.is_teacher:
            messages.warning(request, "Only teachers can create groups. Please contact chris@unfoldstudio.net if you would like to be upgraded to teacher role.")
            return redirect('list_groups')
            
        group = LiteracyGroup(site=get_current_site(request))
        form = self.get_form_class()(request.POST, instance=group)
        if form.is_valid():
            group = form.save()
            group.members.add(request.user)
            group.leaders.add(request.user)
            log.info(name = "Literacy Groups Alert", event="New Litaracy Group Created", args={"user": request.user, "group_name": group.name, "group_id": group.id})
            return redirect('show_group', group.id)
        else:
            context = self.get_context_data(form=form)
            return render('literacy_groups/literacygroup_form.html', context=context)

class UpdateGroupView(LiteracyGroupContextMixin, UpdateView):
    fields = ['name', 'anyone_can_join']
    url_group_key = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edit group"
        return context

    def get_queryset(self):
        return LiteracyGroup.objects.filter(site=get_current_site(self.request))

    def get_success_url(self):
        return reverse('show_group', args=(self.group.id,))

class ShowGroupView(LiteracyGroupContextMixin, DetailView):
    context_object_name = 'group'
    url_group_key = 'pk'
    require_member = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leader'] = self.user_is_leader
        context['prompts'] = self.group.prompts.filter(deleted=False).all()
        return context

    def get_queryset(self):
        return LiteracyGroup.objects.filter(site=get_current_site(self.request))

    def get_template_names(self):
        if self.user_is_member:
            return ['literacy_groups/literacygroup_detail.html']
        else:
            return ['literacy_groups/literacygroup_detail_not_member.html']


class InviteToGroupView(LiteracyGroupContextMixin, DetailView):
    template_name = "literacy_groups/invite.html"
    url_group_key = "pk"
    require_leader = True
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        context['leader'] = self.user_is_leader
        context['join_url'] = self.request.build_absolute_uri(reverse('join_group', args=(self.group.id,)))
        if not self.group.anyone_can_join:
            context['join_url'] += '?code={}'.format(self.group.join_code)
        return context
        
    def get_queryset(self):
        return LiteracyGroup.objects.filter(site=get_current_site(self.request))

class ChangeGroupInviteView(LiteracyGroupContextMixin, View):
    url_group_key = "pk"
    require_leader = True
    allowed_methods = ['post']

    def post(self, request, *args, **kwargs):
        self.group.join_code = self.group.new_join_code()
        self.group.save()
        messages.info(request, "The group invite link has been changed.")
        return redirect('invite_to_group', self.group.id)

class JoinGroupView(LiteracyGroupContextMixin, View):
    url_group_key = "pk"
    require_member = False

    def get(self, request, *args, **kwargs):
        if self.group in request.user.literacy_groups.all():
            messages.warning(request, "You're already a member of {}".format(self.group.name))
            log.warning(name = "Literacy Groups Alert", event= "Failed Joining Group", msg ="User Already Member",
                         args={"user": request.user, "group_name": self.group.name, "group_id": self.group.id})
        elif not self.group.anyone_can_join and request.GET.get('code') != self.group.join_code:
            messages.warning(request, "Wrong code")
            log.warning(name = "Literacy Groups Alert", event= "Failed Joining Group", msg= "User Provided Wrong Code", 
                        args={"user": request.user, "group_name": self.group.name, "group_id": self.group.id})
        else:
            request.user.literacy_groups.add(self.group)
            messages.success(request, "Joined {}".format(self.group.name))
            log.info(name = "Literacy Groups Alert", event= "New User Joined Literacy Group", args={
                "user": request.user, "group_name": self.group.name, "group_id": self.group.id})
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.JOINED_LITERACY_GROUP,
                subject=request.user,
                literacy_group=self.group,
            )
        return redirect('show_group', self.group.id)

class LeaveGroupView(LiteracyGroupContextMixin, View):
    url_group_key = "pk"

    def post(self, request, *args, **kwargs):
        if self.group not in request.user.literacy_groups.all():
            messages.warning(request, "You're not a member of {}".format(self.group.name))
            log.warning(name = "Literacy Groups Alert", event= "Failed Leaving Group", msg="User not a member",
                         args={"user": request.user, "group_name": self.group.name, "group_id": self.group.id})
        elif self.group in request.user.literacy_groups_leading.all():
            messages.warning(request, "You can't leave groups you lead".format(self.group.name))
            log.warning(name = "Literacy Groups Alert", event= "Failed Leaving Group", msg= "User is Leader", args={
                "user": request.user, "group_name": self.group.name, "group_id": self.group.id})
        else:
            request.user.literacy_groups.remove(self.group)
            messages.success(request, "Left {}".format(self.group.name))
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.LEFT_LITERACY_GROUP,
                subject=request.user,
                literacy_group=self.group,
            )
            log.info(name = "Literacy Groups Alert", event= "Member Left", args={
                "user": request.user, "group_name": self.group.name, "group_id": self.group.id})
        if request.user.literacy_groups.exists():
            return redirect('list_groups')
        else:
            return redirect('home')

