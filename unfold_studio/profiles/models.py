from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import arrow

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField('auth.User', related_name='profile', on_delete=models.CASCADE)
    birth_month = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=100, null=True, blank=True)
    following = models.ManyToManyField('profiles.Profile', related_name='followers', blank=True)
    is_teacher = models.BooleanField(default=False)
    is_researcher = models.BooleanField(default=False)
    profile_story = models.ForeignKey(
        'unfold_studio.Story',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='profile_featured_by',
    )

    def __str__(self):
        return self.user.username


class DeprecatedUsername(models.Model):
    """Records usernames that have been reassigned, so they cannot be reclaimed."""
    old_username = models.CharField(max_length=150, unique=True, db_index=True)
    new_username = models.CharField(max_length=150)
    renamed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.old_username} → {self.new_username}'

