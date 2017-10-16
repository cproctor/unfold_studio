from django.db import models 
from .helpers import compile_ink
from django.contrib import admin
from django.contrib.auth.models import User
from profiles.models import Profile

class Story(models.Model):
    """
    Stories can be saved even if invalid.

    """
    title = models.CharField(max_length=400)
    author = models.ForeignKey(User)
    #creation_date = models.DateTimeField('date created')
    #edit_date = models.DateTimeField('date changed')
    #view_count = models.IntegerField(default=0)
    ink = models.TextField(blank=True)
    json = models.TextField(blank=True)
    status = models.CharField(max_length=100, blank=True)
    message = models.CharField(max_length=400, blank=True)
    err_line = models.IntegerField(blank=True, null=True)
    shared=models.BooleanField(default=False)
    featured=models.BooleanField(default=False)
    loves = models.ManyToManyField(Profile, related_name="loved_stories")

    def __str__(self):
        return "{} by {}".format(self.title, self.author)

    def compile_ink(self):
        compiled_ink = compile_ink(self.ink)
        self.status = compiled_ink['status']
        self.message = compiled_ink['message']
        self.err_line = compiled_ink.get('line')
        if compiled_ink.get('result'):
            self.json = compiled_ink['result']

class Book(models.Model):
    title = models.CharField(max_length=400)
    owner = models.ForeignKey(User)
    stories = models.ManyToManyField(Story)
        
admin.site.register(Story)
