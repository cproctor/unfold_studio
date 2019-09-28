from django.db import models
from django.contrib.auth.models import User, Group
from unfold_studio.models import Book
from reversion.models import Version
from django.utils import timezone
from django.contrib.sites.models import Site

class PromptManager(models.Manager):
    """
    Extends the default Manager for Prompts, adding additional queries
    """
    def unsubmitted_for_user(self, user):
        results = self.get_queryset().filter(deleted=False)
        results = results.filter(literacy_group__members=user)
        results = results.exclude(submissions__author=user)
        return results

class Prompt(models.Model):
    name = models.CharField(max_length=400)
    author = models.ForeignKey(User, on_delete="cascade", null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    literacy_group = models.ForeignKey("literacy_groups.LiteracyGroup", related_name="prompts", on_delete="cascade", 
            null=True)
    description = models.TextField(blank=True)
    submissions = models.ManyToManyField('unfold_studio.Story', through='prompts.PromptStory', 
            related_name='prompts_submitted')
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, blank=True, null=True, related_name="prompts")

    objects = PromptManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-due_date']

class PromptStory(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    story = models.ForeignKey('unfold_studio.Story', on_delete=models.CASCADE)
    submitted_story_version = models.ForeignKey(Version, on_delete=models.CASCADE)

    class Meta:
        unique_together = [('prompt', 'story')]
        verbose_name_plural = "Prompt stories"
