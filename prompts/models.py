from django.db import models
from django.contrib.auth.models import User, Group
from reversion.models import Version
from django.utils import timezone

# Create your models here.
class Prompt(models.Model):
    name = models.CharField(max_length=400)
    creation_date = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)
    due_date = models.DateTimeField(auto_now=True)
    owners = models.ManyToManyField(User, related_name='prompts_owned')
    assignee_groups = models.ManyToManyField(Group, related_name='prompts_assigned', blank=True)
    description = models.TextField(blank=True)
    submissions = models.ManyToManyField('unfold_studio.Story', through='prompts.PromptStory', 
            related_name='prompts_submitted')

    def __str__(self):
        return self.name

    @property
    def assignees(self):
        return User.objects.filter(groups__prompts_assigned=self)

    class Meta:
        ordering = ['-due_date']

class PromptStory(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    story = models.ForeignKey('unfold_studio.Story', on_delete=models.CASCADE)
    submitted_story_version = models.ForeignKey(Version, on_delete=models.CASCADE)

    class Meta:
        unique_together = [('prompt', 'story')]
        verbose_name_plural = "Prompt stories"
