from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
import arrow

class LiteracyEventManager(models.Manager):
    def similar(self, e):
        "Returns all similar events"
        return LiteracyEvent.objects.filter(
            event_type=e.event_type, 
            subject=e.subject,
            story=e.story,
            book=e.book,
            prompt=e.prompt,
            object_user=e.object_user
        )

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
    UNPUBLISHED_STORY               = 'b'
    PUBLISHED_BOOK                  = '4'
    ADDED_STORY_TO_BOOK             = '5'
    REMOVED_STORY_FROM_BOOK         = '9'
    FOLLOWED                        = '6'
    UNFOLLOWED                      = 'a'
    SIGNED_UP                       = '8'
    CREATED_PROMPT                  = 'c'
    SUBMITTED_TO_PROMPT             = 'd'
    UNSUBMITTED_FROM_PROMPT         = 'e'

    EVENT_TYPES = (
        (LOVED_STORY, "loved story"),
        (COMMENTED_ON_STORY, "commented on story"),
        (FORKED_STORY, "forked a story"),
        (PUBLISHED_STORY, "published story"),
        (PUBLISHED_STORY, "unpublished story"),
        (PUBLISHED_BOOK, "published book"),
        (ADDED_STORY_TO_BOOK, "added story to book"),
        (REMOVED_STORY_FROM_BOOK, "removed story from book"),
        (FOLLOWED, "followed"),
        (UNFOLLOWED, "unfollowed"),
        (SIGNED_UP, "signed up"),
        (CREATED_PROMPT, "created prompt"),
        (SUBMITTED_TO_PROMPT, "submitted to prompt"),
        (UNSUBMITTED_FROM_PROMPT, "unsubmitted from prompt")
    )
    
    timestamp = models.DateTimeField(default=timezone.now)
    event_type = models.CharField(max_length=1, choices=EVENT_TYPES)
    subject = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='literacy_events')
    book = models.ForeignKey('unfold_studio.Book', null=True, blank=True, on_delete=models.CASCADE, 
            related_name='literacy_events')
    story = models.ForeignKey('unfold_studio.Story', null=True, blank=True, on_delete=models.CASCADE, 
            related_name='literacy_events')
    prompt = models.ForeignKey('prompts.Prompt', null=True, blank=True, on_delete=models.CASCADE,
            related_name='literacy_events')
    object_user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, 
            related_name='literacy_events_as_object')

    objects = LiteracyEventManager()

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)

    def __str__(self, with_prefix=True):
        prefix = "[{}] ".format(self.subject)
        ts = " ({})".format(arrow.get(self.timestamp).format('H:mm a, MMM DD, YYYY'))
        if self.event_type == LiteracyEvent.LOVED_STORY:
            body = "{} loved story {}".format(self.subject, self.story.title)
        elif self.event_type == LiteracyEvent.COMMENTED_ON_STORY:
            body =  "{} commented on '{}'".format(self.subject, self.story.title)
        elif self.event_type == LiteracyEvent.FORKED_STORY:
            body = "{} forked '{}'".format(self.subject, self.story.title)
        elif self.event_type == LiteracyEvent.PUBLISHED_STORY:
            body = "{} published '{}'".format(self.subject, self.story.title)
        elif self.event_type == LiteracyEvent.UNPUBLISHED_STORY:
            body = "{} unpublished '{}'".format(self.subject, self.story.title)
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
        elif self.event_type == LiteracyEvent.CREATED_PROMPT:
            body = "{} created prompt {}".format(self.subject, self.prompt)
        elif self.event_type == LiteracyEvent.SUBMITTED_TO_PROMPT:
            body = "{} submitted {} to prompt {}".format(self.subject, self.story, self.prompt)
        elif self.event_type == LiteracyEvent.UNSUBMITTED_FROM_PROMPT:
            body = "{} unsubmitted {} from prompt {}".format(self.subject, self.story, self.prompt)
        else:
            raise ValueError("Unhandled event type: {}".format(self.event_type))
        return (prefix if with_prefix else '') + body + ts

    class Meta:
        indexes = [models.Index(fields=['subject', 'timestamp'])]
        ordering = ('-timestamp',)

class NotificationManager(models.Manager):

    def valid_notifications(self):
        "Returns notifications for which no subject or object is disabled or deleted"
        return self.get_queryset().filter(
            (Q(event__story__deleted=False) & Q(event__story__author__is_active=True)) | Q(event__story__isnull=True),
            (Q(event__book__deleted=False) & Q(event__book__owner__is_active=True)) | Q(event__book__isnull=True),
            Q(event__subject__is_active=True) | Q(event__subject__isnull=True),
            Q(event__object_user__is_active=True) | Q(event__object_user__isnull=True)
        )

    def for_user(self, user):
        "Returns notifications that ought to be in the user's feed."
        return self.valid_notifications().filter(recipient=user)

    def mark_all_seen_for_user(self, user):
        for e in self.get_queryset().filter(recipient=user, seen=False).iterator(chunk_size=500):
            e.seen = True
            e.save()

class Notification(models.Model):
    """
    Represents notifications that appear in users' feeds. Each LiteracyEvent generates zero, one, or multiple notifications.
    """
    recipient = models.ForeignKey('auth.User', related_name='notifications', on_delete=models.CASCADE)
    event = models.ForeignKey(LiteracyEvent, on_delete=models.CASCADE, related_name='notifications')
    seen = models.BooleanField(default=False)

    objects = NotificationManager()

    def __str__(self):
        return "{} notification for {}: {}".format("Seen" if self.seen else "Unseen", 
                self.recipient, self.event.__str__(with_prefix=False))

    class Meta:
        ordering = ('-event__timestamp',)
