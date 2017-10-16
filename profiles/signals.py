from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from unfold_studio.models import Story, Book
from profiles.models import Profile, Event

# Currently, no events are generated for ADDED_STORY_TO_BOOK, COMMENTED_ON_STORY, FORKED_STORY

def get_related(instance, pk_set, model, reverse, **kwargs):
    "Given kwargs for a m2m relation, returns a tuple of tuples of forward relations"
    if reverse:
        return ((model.objects.get(pk=id), instance) for id in pk_set)
    else:
        return ((instance, model.objects.get(pk=id)) for id in pk_set)

@receiver(m2m_changed, sender=Story.loves.through, dispatch_uid="create_loved_story_events")
def create_loved_story_events(sender, **kwargs):
    "When someone loves a story, creates event for the story's author"
    if kwargs['action'] == 'post_add':
        for story, profile in get_related(**kwargs):
            Event.objects.create(
                user = story.author,
                subject = profile.user,
                event_type = Event.LOVED_STORY,
                story = story
            )

@receiver(post_save, sender=Story, dispatch_uid="create_story_forked_events")
def create_story_forked_events(sender, **kwargs):
    "When a story is forked, creates events for the story's author"
    story = kwargs['instance']
    if story.parent is not None:
        Event.objects.create(
            user=story.parent.author,
            subject=story.author,
            event_type=Event.FORKED_STORY,
            story=story
        )
        
@receiver(post_save, sender=Story, dispatch_uid="create_story_published_events")
def create_story_published_events(sender, **kwargs):
    "When a story is shared, creates events for all current followers of the author"
    story = kwargs['instance']
    if story.shared:
        for follower_profile in story.author.profile.followers.all():
            Event.objects.create(
                user=follower_profile.user,
                subject=story.author,
                event_type=Event.PUBLISHED_STORY,
                story=story
            )
                
@receiver(post_save, sender=Book, dispatch_uid="create_book_published_events")
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
