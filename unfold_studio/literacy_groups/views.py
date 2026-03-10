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
    fields = ['name']

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
            log.info(name = "Literacy Groups Alert", event="New Literacy Group Created", args={"user": request.user, "group_name": group.name, "group_id": group.id})
            return redirect('show_group', group.id)
        else:
            context = self.get_context_data(form=form)
            return render('literacy_groups/literacygroup_form.html', context=context)

class UpdateGroupView(LiteracyGroupContextMixin, UpdateView):
    fields = ['name']
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
        context['join_codes'] = self.group.codes.all().select_related('assigned_user')
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
        code_str = request.GET.get('code')

        #Check if code exists for this group
        try: 
            join_code = JoinCode.objects.get(code=code_str, group=self.group)
        except JoinCode.DoesNotExist:
            messages.warning(request, "Invalid Join Code.")
            return redirect('home')
        
        #Check if code is taken by someone else
        if join_code.assigned_user and join_code.assigned_user != request.user:
            messages.warning(request, "This code has already been used.")
            return redirect('home')
        
        #Join the group and link the code
        request.user.literacy_groups.add(self.group)
        join_code.assigned_user = request.user
        join_code.save()

        #Log the event
        LiteracyEvent.objects.create(   
            event_type=LiteracyEvent.JOINED_LITERACY_GROUP,
            subject=request.user,
            literacy_group=self.group,
        )
        
        messages.success(request, "Joined {}".format(self.group.name))
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
            #find the code the student used and free it
            JoinCode.objects.filter(group=self.group, assigned_user=request.user).update(assigned_user=None)
            #Remove the student from the group
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

class DeleteJoinCodeView(LiteracyGroupContextMixin, View):
    url_group_key = "pk"
    require_leader = True

    def post(self, request,pk, code_id, *args, **kwargs):
        
        try:
            # We filter by group to ensure a teacher can't delete a code from another group
            join_code = JoinCode.objects.get(id=code_id, group_id=pk)
            
            # If a student is linked, remove them from the group
            if join_code.assigned_user:
                student = join_code.assigned_user
                self.group.members.remove(student)
                messages.info(request, f"Removed {student.username} and deleted their code.")
            else:
                messages.info(request, "Unused code deleted.")
                
            join_code.delete()
        except JoinCode.DoesNotExist:
            messages.error(request, "Code not found.")
            
        return redirect('invite_to_group', pk)

class GenerateCodesView(LiteracyGroupContextMixin, View):
    url_group_key = "pk"
    require_leader = True

    def post(self, request, *args, **kwargs):
        num_codes = int(request.POST.get('quantity', 5)) # Default to 5
        for _ in range(num_codes):
            JoinCode.objects.create(
                group=self.group,
                code=self.group.new_join_code() # Uses existing random generator
            )
        messages.success(request, f"Generated {num_codes} new codes.")
        return redirect('invite_to_group', self.group.id)