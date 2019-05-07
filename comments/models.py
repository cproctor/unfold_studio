from django.db import models
from django.contrib.auth.models import User
from unfold_studio.models import Story
from django.db.models import Q
from django.utils import timezone

class CommentManager(models.Manager):

    def for_story(self, story):
        if not story.author:
            return self.get_queryset().none()
        else:
            return self.get_queryset().filter(deleted=False, story=story).filter(
                Q(author=story.author) | 
                Q(author__profile__followers=story.author.profile) | 
                Q(author__prompts_owned__submissions=story)
            ).distinct()

# Create your models here.
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="comments")
    creation_date = models.DateTimeField('date created', default=timezone.now)
    message = models.TextField()
    deleted = models.BooleanField(default=False)
    
    objects = CommentManager()

    def __str__(self):
        return '{} commented on {}, "{}"'.format(
            self.author, 
            self.story, 
            self.message[:20] + '...' if len(self.message) > 20 else self.message
        )
