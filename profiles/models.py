from django.db import models
from django.utils import timezone
import arrow

# Create your models here.
class Profile(models.Model):    
    user = models.OneToOneField('auth.User', related_name='profile')
    birth_month = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=100, null=True, blank=True)
    following = models.ManyToManyField('profiles.Profile', related_name='followers', blank=True)

    def __str__(self):
        return self.user.username

class Event(models.Model):
    "Things that show up in a user's feed"

    LOVED_STORY = '0'
    COMMENTED_ON_STORY = '1'
    FORKED_STORY = '2'
    PUBLISHED_STORY = '3'
    PUBLISHED_BOOK = '4'
    ADDED_STORY_TO_BOOK = '5'
    FOLLOWED = '6'
    YOU_FOLLOWED = '7'

    EVENT_TYPES = (
        (LOVED_STORY, "loved story"),
        (COMMENTED_ON_STORY, "commented on story"),
        (FORKED_STORY, "forked a story"),
        (PUBLISHED_STORY, "published story"),
        (PUBLISHED_BOOK, "published book"),
        (ADDED_STORY_TO_BOOK, "added story to book"),
        (FOLLOWED, "followed"),
        (YOU_FOLLOWED, "you followed")
    )
    
    user = models.ForeignKey('auth.User', related_name='events')
    timestamp = models.DateTimeField(default=timezone.now)
    event_type = models.CharField(max_length=1, choices=EVENT_TYPES)
    subject = models.ForeignKey('auth.User')
    book = models.ForeignKey('unfold_studio.Book', null=True, blank=True)
    story = models.ForeignKey('unfold_studio.Story', null=True, blank=True)

    def __str__(self):
        prefix = "[{}] ".format(self.user)
        ts = " ({})".format(arrow.get(self.timestamp).format('H:mm a, MMM DD, YYYY'))
        if self.event_type == Event.LOVED_STORY:
            body = "{} loved story {}".format(self.subject, self.story.title)
        elif self.event_type == Event.COMMENTED_ON_STORY:
            body =  "{} commented on '{}'".format(self.subject, self.story.title)
        elif self.event_type == Event.FORKED_STORY:
            body = "{} forked '{}'".format(self.subject, self.story.title)
        elif self.event_type == Event.PUBLISHED_STORY:
            body = "{} published '{}'".format(self.subject, self.story.title)
        elif self.event_type == Event.PUBLISHED_BOOK:
            body = "{} published book '{}'".format(self.subject, self.book)
        elif self.event_type == Event.ADDED_STORY_TO_BOOK:
            body = "{} added '{}' to '{}'".format(self.subject, self.story.title, self.book)
        elif self.event_type == Event.FOLLOWED:
            body = "{} now follows you".format(self.subject)
        elif self.event_type == Event.YOU_FOLLOWED:
            body = "You now follow {}".format(self.subject)
        return prefix + body + ts

    class Meta:
        # Ensures no duplication of events
        unique_together = (('user', 'event_type', 'subject', 'book', 'story'), )
        indexes = [models.Index(fields=['user', 'timestamp'])]
        ordering = ('timestamp',)

