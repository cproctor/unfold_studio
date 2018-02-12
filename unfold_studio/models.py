from django.db import models 
from .helpers import compile_ink
from django.contrib.auth.models import User
from profiles.models import Profile
import reversion
from datetime import datetime, timezone
from django.conf import settings

@reversion.register()
class Story(models.Model):
    """
    Stories can be saved even if invalid.

    """
    title = models.CharField(max_length=400)
    author = models.ForeignKey(User, related_name='stories', blank=True, null=True)
    creation_date = models.DateTimeField('date created')
    edit_date = models.DateTimeField('date changed')
    #view_count = models.IntegerField(default=0)
    ink = models.TextField(blank=True)
    json = models.TextField(blank=True)
    status = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)
    err_line = models.IntegerField(blank=True, null=True)
    shared=models.BooleanField(default=False)
    public=models.BooleanField(default=False)
    featured=models.BooleanField(default=False)
    loves = models.ManyToManyField(Profile, related_name="loved_stories", blank=True)
    parent = models.ForeignKey("unfold_studio.Story", related_name="children", null=True, blank=True)
    includes = models.ForeignKey("unfold_studio.Story", related_name="included_by", null=True, blank=True)
    deleted = models.BooleanField(default=False)
    priority = models.FloatField(default=0)

    def __str__(self):
        return "{} by {}".format(self.title, self.author)

    def compile_ink(self):
        compiled_ink = compile_ink(self.ink, self.id)
        self.status = compiled_ink['status']
        self.message = compiled_ink['message']
        self.err_line = compiled_ink.get('line')
        if compiled_ink.get('result'):
            self.json = compiled_ink['result']

    # Using Hacker News gravity algorithm: 
    # https://medium.com/hacking-and-gonzo/how-hacker-news-ranking-algorithm-works-1d9b0cf2c08d
    def update_priority(self):
        score = (1 + 
            self.loves.count() * settings.FEATURED['LOVE_SCORE'] + 
            self.books.count() * settings.FEATURED['BOOK_SCORE'] + 
            self.children.count() * settings.FEATURED['FORK_SCORE'] + 
            int(self.featured) * settings.FEATURED['FEATURED_SCORE']
        )
        age_in_hours = (datetime.now(timezone.utc) - self.edit_date).total_seconds() / (60 * 60)
        self.priority = score / pow(age_in_hours + 2, settings.FEATURED['GRAVITY'])

    class Meta:
        ordering = ['-priority']
    
class Book(models.Model):
    title = models.CharField(max_length=400)
    owner = models.ForeignKey(User)
    stories = models.ManyToManyField(Story, related_name='books')
