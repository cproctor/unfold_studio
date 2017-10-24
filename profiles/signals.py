from django.db.models import signals
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from unfold_studio.models import Story, Book
from profiles.models import Profile, Event
from django.conf import settings
from django.utils.text import get_text_list
from django.db import connection, IntegrityError
from django.utils.translation import ugettext as _

# Currently, no events are generated for ADDED_STORY_TO_BOOK, COMMENTED_ON_STORY, FORKED_STORY

def catch_integrity_error(fn):
    def new_fn(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except IntegrityError:
            pass
    new_fn.__name__ = fn.__name__
    return new_fn

def get_related(instance, pk_set, model, reverse, **kwargs):
    "Given kwargs for a m2m relation, returns a tuple of tuples of forward relations"
    if reverse:
        return ((model.objects.get(pk=id), instance) for id in pk_set)
    else:
        return ((instance, model.objects.get(pk=id)) for id in pk_set)

@receiver(m2m_changed, sender=Story.loves.through, dispatch_uid="create_loved_story_events")
@catch_integrity_error
def create_loved_story_events(sender, **kwargs):
    "When someone loves a story, creates event for the story's author"
    if kwargs['action'] == 'post_add':
        for story, profile in get_related(**kwargs):
            if story.author:
                Event.objects.create(
                    user = story.author,
                    subject = profile.user,
                    event_type = Event.LOVED_STORY,
                    story = story
                )

@receiver(post_save, sender=Story, dispatch_uid="create_story_forked_events")
@catch_integrity_error
def create_story_forked_events(sender, **kwargs):
    "When a story is forked, creates events for the story's author"
    story = kwargs['instance']
    if story.parent and story.author and story.parent.author:
        Event.objects.create(
            user=story.parent.author,
            subject=story.author,
            event_type=Event.FORKED_STORY,
            story=story
        )
        
@receiver(post_save, sender=Story, dispatch_uid="create_story_published_events")
@catch_integrity_error
def create_story_published_events(sender, **kwargs):
    "When a story is shared, creates events for all current followers of the author"
    story = kwargs['instance']
    if story.shared and story.author:
        for follower_profile in story.author.profile.followers.all():
            Event.objects.create(
                user=follower_profile.user,
                subject=story.author,
                event_type=Event.PUBLISHED_STORY,
                story=story
            )
                
@receiver(post_save, sender=Book, dispatch_uid="create_book_published_events")
@catch_integrity_error
def create_book_published_events(sender, **kwargs):
    "When a book is created, creates events for all current followers of the author"
    book = kwargs['instance']
    if kwargs['created']:
        for follower_profile in book.owner.profile.followers.all():
            Event.objects.create(
                user=follower_profile.user,
                subject=book.owner,
                event_type=Event.PUBLISHED_BOOK,
                book=book
            )

@receiver(m2m_changed, sender=Profile.following.through, dispatch_uid="create_followed_events")
@catch_integrity_error
def create_followed_events(sender, **kwargs):
    "When a new follower relation is added, creates an event for both parties"
    if kwargs['action'] == 'post_add':
        for follower, followed in get_related(**kwargs):
            Event.objects.create(
                user=follower.user,
                subject=followed.user,
                event_type=Event.YOU_FOLLOWED
            )
            Event.objects.create(
                user=followed.user,
                subject=follower.user,
                event_type=Event.FOLLOWED
            )


# https://djangosnippets.org/snippets/1628/
def check_unique_together(sender, **kwargs):
    """
    Check models unique_together manually. Django enforced unique together only the database level, but
    some databases (e.g. SQLite) doesn't support this.
    """
    instance = kwargs["instance"]
    for field_names in sender._meta.unique_together:
        model_kwargs = {}
        for field_name in field_names:
            try:
                data = getattr(instance, field_name)
            except FieldDoesNotExist:
                # e.g.: a missing field, which is however necessary.
                # The real exception on model creation should be raised. 
                continue
            model_kwargs[field_name] = data

        query_set = sender.objects.filter(**model_kwargs)
        if instance.pk != None:
            # Exclude the instance if it was saved in the past
            query_set = query_set.exclude(pk=instance.pk)

        count = query_set.count()
        if count > 0:
            field_names = get_text_list(field_names, _('and'))
            msg = _(u"%(model_name)s with this %(field_names)s already exists.") % {
                'model_name': instance.__class__.__name__,
                'field_names': field_names
            }
            raise IntegrityError(msg)

if connection.vendor == 'sqlite':
    signals.pre_save.connect(check_unique_together, sender=Event)
