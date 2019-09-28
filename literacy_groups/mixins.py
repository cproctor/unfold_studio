from django.contrib.auth.mixins import LoginRequiredMixin
from literacy_groups.models import LiteracyGroup
from django.shortcuts import redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.views import View
from django.contrib import messages

class LiteracyGroupContextMixin(LoginRequiredMixin, View):
    """
    Updates the setup method to ensure the user is in the group, and adds the group as 
    an instance attribute
    """
    url_group_key = "group_pk"
    require_member = True
    require_leader = False

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if self.require_member:
            self.group = get_object_or_404(LiteracyGroup, pk=kwargs[self.url_group_key], members=request.user, 
                    site=get_current_site(request), deleted=False)
        else:
            self.group = get_object_or_404(LiteracyGroup, pk=kwargs[self.url_group_key], 
                    site=get_current_site(request), deleted=False)
        self.user_is_leader = self.group in request.user.literacy_groups_leading.all()
        self.user_is_member = self.group in request.user.literacy_groups.all()
        if self.require_leader and not self.user_is_leader:
            messages.warning("Only group leaders can do this.")
            return redirect('show_group', self.group.id)
