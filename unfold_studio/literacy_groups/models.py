from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from commons.base.models import SoftDeleteMixin


class LiteracyGroup(SoftDeleteMixin):
    """
    A LiteracyGroup models a classroom, writing club, or another space.
    """
    name = models.TextField()
    members = models.ManyToManyField(User, related_name="literacy_groups")
    leaders = models.ManyToManyField(User, related_name="literacy_groups_leading")
    join_code = models.TextField()

    def __str__(self):
        return self.name

    def new_join_code(self):
        "Returns a new join code"
        return get_random_string(length=8).upper()


class JoinCode(models.Model):
    """A single-use code that lets a student create an account and join a group in one step."""
    group = models.ForeignKey(LiteracyGroup, on_delete=models.CASCADE, related_name="codes")
    code = models.CharField(max_length=10, unique=True)
    assigned_user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="used_join_code"
    )

    def __str__(self):
        return f"{self.code} ({'used' if self.assigned_user_id else 'unused'})"
