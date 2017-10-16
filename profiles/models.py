from django.db import models

# Create your models here.
class Profile(models.Model):    
    user = models.OneToOneField('auth.User', related_name='profile')
    birth_month = models.DateField()
    gender = models.CharField(max_length=100)
    following = models.ManyToManyField('profiles.Profile', related_name='followers')

