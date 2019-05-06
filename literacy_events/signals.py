# NOTE These signal handlers are all currently disabled (see literacy_events/apps.py). 
# They are not behaving as intended; I plan to rework the funcitonality and stop using signals
# for most interaction. Instead view code will manually create LiteracyEvents as appropriate. 
# I know this creates a tight coupling, but that coupling already exists in more cryptic form in 
# the buggy logic encoded below. 

# I will continue to use signals to create notifications in response to event creation. 

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from literacy_events.models import LiteracyEvent, Notification
import logging

log = logging.getLogger(__name__)    

@receiver(post_save, sender=LiteracyEvent, weak=False, dispatch_uid="literacy_event_notification")
def literacy_event_notifications(sender, **kwargs):
    event = kwargs['instance']
    for user in get_recipients(event):
        n = Notification.objects.create(recipient=user, event=event)
        log.debug("Created notification: {}".format(n))
    
def get_recipients(e):
    if e.event_type == LiteracyEvent.LOVED_STORY:
        return set(subject(e) + story_author(e) + followers(subject(e)))
    elif e.event_type == LiteracyEvent.COMMENTED_ON_STORY:
        return set(subject(e) + story_author(e))
    elif e.event_type == LiteracyEvent.FORKED_STORY:
        return set(subject(e) + parent_story_author(e) + followers(subject(e)))
    elif e.event_type == LiteracyEvent.PUBLISHED_STORY:
        return set(subject(e) + if_first(e, followers(subject(e))))
    elif e.event_type == LiteracyEvent.UNPUBLISHED_STORY:
        return subject(e)
    elif e.event_type == LiteracyEvent.PUBLISHED_BOOK:
        return set(subject(e) + followers(subject(e)))
    elif e.event_type == LiteracyEvent.ADDED_STORY_TO_BOOK:
        return set(subject(e) + book_owner(e) + followers(subject(e)))
    elif e.event_type == LiteracyEvent.REMOVED_STORY_FROM_BOOK:
        return subject(e)
    elif e.event_type == LiteracyEvent.FOLLOWED:
        return set(subject(e) + if_first(e, object_user(e)))
    elif e.event_type == LiteracyEvent.UNFOLLOWED:
        return subject(e)
    elif e.event_type == LiteracyEvent.SIGNED_UP:
        return subject(e)
    elif e.event_type == LiteracyEvent.CREATED_PROMPT:
        return subject(e)
    elif e.event_type == LiteracyEvent.SUBMITTED_TO_PROMPT:
        return set(subject(e) + prompt_owners(e))
    elif e.event_type == LiteracyEvent.UNSUBMITTED_FROM_PROMPT:
        return set(subject(e) + prompt_owners(e))
    elif e.event_type == LiteracyEvent.STORY_READING:
        return []
    elif e.event_type == LiteracyEvent.PUBLISHED_PROMPT_AS_BOOK:
        return subject(e)
    elif e.event_type == LiteracyEvent.UNPUBLISHED_PROMPT_AS_BOOK:
        return subject(e)
    elif e.event_type == LiteracyEvent.TAGGED_STORY_VERSION:
        if e.story.shared:
            return set(subject(e) + followers(subject(e)))
        else:
            return subject(e)
    else:
        log.debug("No notifications created for {}".format(e))
        return []

def subject(e):
    return [e.subject]

def story_author(e):
    return [e.story.author] if e.story and e.story.author else []

def parent_story_author(e):
    if e.story and e.story.parent and e.story.parent.author:
        return [e.story.parent.author]
    else:
        return []

def book_owner(e):
    return [e.book.owner] if e.book else []

def object_user(e):
    return [e.object_user] if e.object_user else []

def prompt_owners(e):
    return list(e.prompt.owners.all()) if e.prompt else []

def followers(users):
    return list(User.objects.filter(profile__following__user__in=users).distinct())

def if_first(e, users):
    "Returns users only if e is the first occurrence of the event"
    if LiteracyEvent.objects.similar(e).count() == 1:
        return users
    else:
        return []
