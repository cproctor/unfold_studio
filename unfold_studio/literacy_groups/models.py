from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

# Create your models here.
class LiteracyGroup(models.Model):
    """
    A LiteracyGroup models a classroom, writing club, or another space.
    """
    name = models.TextField()
    anyone_can_join = models.BooleanField(default=False)
    members = models.ManyToManyField(User, related_name="literacy_groups")
    leaders = models.ManyToManyField(User, related_name="literacy_groups_leading")
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    join_code = models.TextField()
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def new_join_code(self):
        "Returns a new join code"
        return get_random_string(length=8).upper()


class JoinCode(models.Model):
    group = models.ForeignKey(LiteracyGroup, on_delete=models.CASCADE, related_name="codes")
    code = models.CharField(max_length=10, unique=True)
    assigned_user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="used_join_code")

    def __str__(self):
        return f"{self.code} ({self.assigned_user.username if self.assigned_user else 'Unused'})"


