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

    def __str__(self):
        return self.user.username

