from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class LiteracyEvent(models.Model):
    """
    Represents significant things that happen at the user level.
    """
    # TODO: add new events: created_prompt, submitted_story_to_prompt, read_knot (will require session, ,storyVersion, knot)
    # TODO: Created story, savedStoryVersion

    LOVED_STORY                     = '0'
    COMMENTED_ON_STORY              = '1'
    FORKED_STORY                    = '2'
    PUBLISHED_STORY                 = '3'
    PUBLISHED_BOOK                  = '4'
    ADDED_STORY_TO_BOOK             = '5'
    FOLLOWED                        = '6'
    UNFOLLOWED                      = 'a'
    SIGNED_UP                       = '8'
    REMOVED_STORY_FROM_BOOK         = '9'

    EVENT_TYPES = (
        (LOVED_STORY, "loved story"),
        (COMMENTED_ON_STORY, "commented on story"),
        (FORKED_STORY, "forked a story"),
        (PUBLISHED_STORY, "published story"),
        (PUBLISHED_BOOK, "published book"),
        (ADDED_STORY_TO_BOOK, "added story to book"),
        (REMOVED_STORY_FROM_BOOK, "removed story from book"),
        (FOLLOWED, "followed"),
        (UNFOLLOWED, "unfollowed"),
        (SIGNED_UP, "signed up")
    )
    
    timestamp = models.DateTimeField(default=timezone.now)
    event_type = models.CharField(max_length=1, choices=EVENT_TYPES)
    subject = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='literacy_events')
    book = models.ForeignKey('unfold_studio.Book', null=True, blank=True, on_delete=models.CASCADE, 
            related_name='literacy_events')
    story = models.ForeignKey('unfold_studio.Story', null=True, blank=True, on_delete=models.CASCADE, 
            related_name='literacy_events')
    object_user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, 
            related_name='literacy_events_as_object')

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)

    def __str__(self):
        prefix = "[{}] ".format(self.user)
        ts = " ({})".format(self.timestamp.strftime('H:mm a, MMM DD, YYYY'))
        if self.event_type == LiteracyEvent.LOVED_STORY:
            body = "{} loved story {}".format(self.subject, self.story.title)
        elif self.event_type == LiteracyEvent.COMMENTED_ON_STORY:
            body =  "{} commented on '{}'".format(self.subject, self.story.title)
        elif self.event_type == LiteracyEvent.FORKED_STORY:
            body = "{} forked '{}'".format(self.subject, self.story.title)
        elif self.event_type == LiteracyEvent.PUBLISHED_STORY:
            body = "{} published '{}'".format(self.subject, self.story.title)
        elif self.event_type == LiteracyEvent.PUBLISHED_BOOK:
            body = "{} published book '{}'".format(self.subject, self.book)
        elif self.event_type == LiteracyEvent.ADDED_STORY_TO_BOOK:
            body = "{} added '{}' to '{}'".format(self.subject, self.story.title, self.book)
        elif self.event_type == LiteracyEvent.REMOVED_STORY_FROM_BOOK:
            body = "{} removed '{}' from '{}'".format(self.subject, self.story.title, self.book)
        elif self.event_type == LiteracyEvent.FOLLOWED:
            body = "{} followed {}".format(self.subject, self.object_user)
        elif self.event_type == LiteracyEvent.UNFOLLOWED:
            body = "{} unfollowed {}".format(self.subject, self.object_user)
        elif self.event_type == LiteracyEvent.SIGNED_UP:
            body = "{} signed up".format(self.subject)
        else:
            raise ValueError("Unhandled event type: {}".format(self.event_type))
        return prefix + body + ts

    class Meta:
        indexes = [models.Index(fields=['subject', 'timestamp'])]
        ordering = ('-timestamp',)

class Notification(models.Model):
    """
    Represents notifications that appear in users' feeds. Each LiteracyEvent generates zero, one, or multiple notifications.
    """
    # TODO: I want to be able to filter events at the model level.
    # TODO Check for non-disabled users.
    recipient = models.ForeignKey('auth.User', related_name='notifications', on_delete=models.CASCADE)
    event = models.ForeignKey(LiteracyEvent, on_delete=models.CASCADE, related_name='notifications')
    seen = models.BooleanField(default=False)




