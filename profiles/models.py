from django.db import models

# Create your models here.
class Profile(models.Model):    
    user = models.OneToOneField('auth.User', related_name='profile')
    birth_month = models.DateField()
    gender = models.CharField(max_length=100)
    following = models.ManyToManyField('profiles.Profile', related_name='followers')

class Event(models.Model):
    "Things that show up in a user's feed"

    LOVED_STORY = '0'
    COMMENTED_ON_STORY = '1'
    PUBLISHED_STORY = '2'
    PUBLISHED_BOOK = '3'
    ADDED_STORY_TO_BOOK = '4'
    FOLLOWED = '5'

    EVENT_TYPES = (
        (LOVED_STORY, "loved story"),
        (COMMENTED_ON_STORY, "commented on story"),
        (PUBLISHED_STORY, "published story"),
        (PUBLISHED_BOOK, "published book"),
        (ADDED_STORY_TO_BOOK, "added story to book"),
        (FOLLOWED, "followed")
    )
    
    user = models.ForeignKey('auth.User', related_name='events')
    timestamp = models.DateTimeField()
    event_type = models.CharField(max_length=1, choices=EVENT_TYPES)
    subject = models.ForeignKey('auth.User')
    book = models.ForeignKey('unfold_studio.Book', null=True)
    story = models.ForeignKey('unfold_studio.Story', null=True)

    class Meta:
        # Ensures no duplication of events
        unique_together = (('user', 'event_type', 'subject', 'book', 'story'),)

