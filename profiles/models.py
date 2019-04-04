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

    def __str__(self):
        return self.user.username

# DEPRECATED! USE LITERACY EVENTS INSTEAD
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
    SIGNED_UP = '8'
    REMOVED_STORY_FROM_BOOK = '9'

    EVENT_TYPES = (
        (LOVED_STORY, "loved story"),
        (COMMENTED_ON_STORY, "commented on story"),
        (FORKED_STORY, "forked a story"),
        (PUBLISHED_STORY, "published story"),
        (PUBLISHED_BOOK, "published book"),
        (ADDED_STORY_TO_BOOK, "added story to book"),
        (REMOVED_STORY_FROM_BOOK, "removed story from book"),
        (FOLLOWED, "followed"),
        (YOU_FOLLOWED, "you followed"),
        (SIGNED_UP, "signed up")
    )
    
    user = models.ForeignKey('auth.User', related_name='events', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    event_type = models.CharField(max_length=1, choices=EVENT_TYPES)
    subject = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    book = models.ForeignKey('unfold_studio.Book', null=True, blank=True, on_delete=models.CASCADE)
    story = models.ForeignKey('unfold_studio.Story', null=True, blank=True, on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)

    def validate_unique(self, exclude=None):
        if Event.objects.exclude(pk=self.id).filter(
            event_type=self.event_type, 
            user_id=self.user_id, 
            subject_id=self.subject_id,
            story_id=self.story_id,
            book_id=self.book_id
        ).exists():
            raise ValidationError("Duplicate event: {}".format(self))

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
        elif self.event_type == Event.REMOVED_STORY_FROM_BOOK:
            body = "{} removed '{}' from '{}'".format(self.subject, self.story.title, self.book)
        elif self.event_type == Event.FOLLOWED:
            body = "{} now follows you".format(self.subject)
        elif self.event_type == Event.YOU_FOLLOWED:
            body = "You now follow {}".format(self.subject)
        elif self.event_type == Event.SIGNED_UP:
            body = "{} signed up".format(self.subject)
        else:
            raise ValueError("Unhandled event type: {}".format(self.event_type))
        return prefix + body + ts

    class Meta:
        # Ensures no duplication of events
        unique_together = (('user', 'event_type', 'subject', 'book', 'story'), )
        indexes = [models.Index(fields=['user', 'timestamp'])]
        ordering = ('-timestamp',)

