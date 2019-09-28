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
    members = models.ManyToManyField(User, related_name="literacy_groups")
    leaders = models.ManyToManyField(User, related_name="literacy_groups_leading")
    site = models.ForeignKey(Site, on_delete="cascade")
    anyone_can_join = models.BooleanField(default=False)
    join_code = models.TextField()
    deleted = models.BooleanField(default=False)

    def new_join_code(self):
        "Returns a new join code"
        return get_random_string(length=8).upper()
    
