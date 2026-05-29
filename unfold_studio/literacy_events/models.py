from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q, Exists, OuterRef, Subquery
from stories.models import Story
from books.models import Book
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

    class EventType(models.TextChoices):
        LOVED_STORY             = 'loved_story',            'Loved story'
        COMMENTED               = 'commented',              'Commented on story'
        FORKED                  = 'forked',                 'Forked a story'
        PUBLISHED_STORY         = 'published_story',        'Published story'
        UNPUBLISHED_STORY       = 'unpublished_story',      'Unpublished story'
        PUBLISHED_BOOK          = 'published_book',         'Published book'
        ADDED_TO_BOOK           = 'added_to_book',          'Added story to book'
        REMOVED_FROM_BOOK       = 'removed_from_book',      'Removed story from book'
        FOLLOWED                = 'followed',               'Followed'
        UNFOLLOWED              = 'unfollowed',             'Unfollowed'
        SIGNED_UP               = 'signed_up',              'Signed up'
        CREATED_PROMPT          = 'created_prompt',         'Created prompt'
        SUBMITTED_TO_PROMPT     = 'submitted_to_prompt',    'Submitted to prompt'
        REMOVED_FROM_PROMPT     = 'removed_from_prompt',    'Removed from prompt'
        READ_STORY              = 'read_story',             'Read story'
        PUBLISHED_AS_BOOK       = 'published_as_book',      'Published prompt as book'
        UNPUBLISHED_BOOK        = 'unpublished_book',       'Unpublished prompt book'
        TAGGED_VERSION          = 'tagged_version',         'Tagged story version'
        JOINED_GROUP            = 'joined_group',           'Joined literacy group'
        LEFT_GROUP              = 'left_group',             'Left literacy group'

    # Legacy single-char constants kept for any code still referencing them directly.
    # Migrate call sites to LiteracyEvent.EventType.LOVED_STORY etc.
    LOVED_STORY             = EventType.LOVED_STORY
    COMMENTED_ON_STORY      = EventType.COMMENTED
    FORKED_STORY            = EventType.FORKED
    PUBLISHED_STORY         = EventType.PUBLISHED_STORY
    UNPUBLISHED_STORY       = EventType.UNPUBLISHED_STORY
    PUBLISHED_BOOK          = EventType.PUBLISHED_BOOK
    ADDED_STORY_TO_BOOK     = EventType.ADDED_TO_BOOK
    REMOVED_STORY_FROM_BOOK = EventType.REMOVED_FROM_BOOK
    FOLLOWED                = EventType.FOLLOWED
    UNFOLLOWED              = EventType.UNFOLLOWED
    SIGNED_UP               = EventType.SIGNED_UP
    CREATED_PROMPT          = EventType.CREATED_PROMPT
    SUBMITTED_TO_PROMPT     = EventType.SUBMITTED_TO_PROMPT
    UNSUBMITTED_FROM_PROMPT = EventType.REMOVED_FROM_PROMPT
    STORY_READING           = EventType.READ_STORY
    PUBLISHED_PROMPT_AS_BOOK    = EventType.PUBLISHED_AS_BOOK
    UNPUBLISHED_PROMPT_AS_BOOK  = EventType.UNPUBLISHED_BOOK
    TAGGED_STORY_VERSION    = EventType.TAGGED_VERSION
    JOINED_LITERACY_GROUP   = EventType.JOINED_GROUP
    LEFT_LITERACY_GROUP     = EventType.LEFT_GROUP

    timestamp = models.DateTimeField(default=timezone.now)
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    # subject is nullable so User records can be deleted (SET_NULL) while preserving
    # event history for research integrity.
    subject = models.ForeignKey('auth.User', null=True, blank=True,
            on_delete=models.SET_NULL, related_name='literacy_events')
    book = models.ForeignKey('unfold_studio.Book', null=True, blank=True, on_delete=models.CASCADE,
            related_name='literacy_events')
    story = models.ForeignKey('unfold_studio.Story', null=True, blank=True, on_delete=models.CASCADE,
            related_name='literacy_events')
    prompt = models.ForeignKey('prompts.Prompt', null=True, blank=True, on_delete=models.CASCADE,
            related_name='literacy_events')
    literacy_group = models.ForeignKey('literacy_groups.LiteracyGroup', null=True, blank=True,
            on_delete=models.CASCADE, related_name='literacy_events')
    object_user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL,
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
    def for_request(self, request):
        storyVisible = Exists(Story.objects.for_user(request.user).filter(pk=OuterRef('event__story_id')))
        parentStoryVisible = Exists(Story.objects.for_user(request.user).filter(pk=OuterRef('event__story__parent__id')))
        stories = Story.objects.filter(pk=OuterRef('story_id')).filter(
            Q(deleted=False) & Q(author__is_active=True)
        )
        books = Book.objects.filter(pk=OuterRef('book_id')).filter(
            Q(deleted=False) & Q(owner__is_active=True)
        )

        literacy_events = LiteracyEvent.objects.filter(
            Q(story_id=Subquery(stories.values('id'))) |
            Q(book_id=Subquery(books.values('id'))) |
            Q(subject_id=request.user) |
            Q(object_user_id=request.user) 
        )
        return self.filter(recipient=request.user).filter(event__in=literacy_events).annotate(story_visible=storyVisible, parent_story_visible=parentStoryVisible)


    def mark_all_seen_for_user(self, user):
        self.filter(recipient=user, seen=False).update(seen=True)

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
