from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q, Exists, OuterRef
from unfold_studio.models import Story
from django.contrib.sites.shortcuts import get_current_site
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
    STORY_READING                   = 'f'
    PUBLISHED_PROMPT_AS_BOOK        = 'g'
    UNPUBLISHED_PROMPT_AS_BOOK      = 'h'
    TAGGED_STORY_VERSION            = 'i'
    JOINED_LITERACY_GROUP           = 'j'
    LEFT_LITERACY_GROUP             = 'k'

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
        (UNSUBMITTED_FROM_PROMPT, "unsubmitted from prompt"),
        (STORY_READING, "story knot read"),
        (PUBLISHED_PROMPT_AS_BOOK, "published prompt as book"),
        (UNPUBLISHED_PROMPT_AS_BOOK, "unpublished prompt as book"),
        (TAGGED_STORY_VERSION, 'tagged a story version'),
        (JOINED_LITERACY_GROUP, 'joined literacy group'),
        (LEFT_LITERACY_GROUP, 'left literacy group'),
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
    literacy_group = models.ForeignKey('literacy_groups.LiteracyGroup', null=True, blank=True,
            on_delete=models.CASCADE, related_name='literacy_events')
    object_user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, 
            related_name='literacy_events_as_object')
    extra = models.TextField(blank=True, null=True)

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
        elif self.event_type == LiteracyEvent.STORY_READING:
            body = "{} read {} with path {}".format(self.subject, self.story, self.extra)
        elif self.event_type == LiteracyEvent.PUBLISHED_PROMPT_AS_BOOK:
            body = "{} published prompt {} as book {}".format(self.subject, self.prompt, self.book)
        elif self.event_type == LiteracyEvent.UNPUBLISHED_PROMPT_AS_BOOK:
            body = "{} unpublished prompt {}".format(self.subject, self.prompt, self.book)
        elif self.event_type == LiteracyEvent.TAGGED_STORY_VERSION:
            body = "{} tagged a version of {}".format(self.subject, self.story)
        elif self.event_type == LiteracyEvent.JOINED_LITERACY_GROUP:
            body = "{} joined group {}".format(self.subject, self.literacy_group)
        elif self.event_type == LiteracyEvent.LEFT_LITERACY_GROUP:
            body = "{} left group {}".format(self.subject, self.literacy_group)
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
            Q(event__object_user__is_active=True) | Q(event__object_user__isnull=True),
            Q(event__literacy_group__deleted=False) | Q(event__literacy_group__isnull=True),
        )

    def for_request(self, request):
        "Returns notifications that ought to be visible for the current request"
        user = request.user
        site = get_current_site(request)
        return self.for_site_user(site, user)

    def for_site_user(self, site, user):
        storyVisible = Exists(Story.objects.for_site_user(site, user).filter(pk=OuterRef('event__story_id')))
        parentStoryVisible = Exists(Story.objects.for_site_user(site, user).filter(
                pk=OuterRef('event__story__parent__id')))
        return self.valid_notifications().filter(recipient=user).annotate(
                story_visible=storyVisible, parent_story_visible=parentStoryVisible)

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
