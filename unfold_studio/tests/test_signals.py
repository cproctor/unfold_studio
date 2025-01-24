from django.test import TestCase
from django.utils.timezone import now
from unfold_studio.models import Story, Book
from profiles.models import Profile
from literacy_events.models import LiteracyEvent
from django.contrib.auth.models import User

class SignalsTestCase(TestCase):
    def setUp(self):
        chris = User.objects.create(username='chris')
        zuz = User.objects.create(username='zuz')
        Profile.objects.create(user=chris)
        Profile.objects.create(user=zuz)
        chris.profile.following.add(zuz.profile)
        s = Story.objects.create(title="My first story", author=zuz, shared=True, creation_date=now(), edit_date=now())

    def test_loved_event_created(self):
        chris = User.objects.get(username='chris')
        zuz = User.objects.get(username='zuz')
        self.assertEqual(LiteracyEvent.objects.filter(user=zuz, event_type=Event.LOVED_STORY).count(), 0)
        zuz.stories.first().loves.add(chris.profile)
        self.assertEqual(LiteracyEvent.objects.filter(user=zuz, event_type=Event.LOVED_STORY).count(), 1)

    def test_forked_event_created(self):
        chris = User.objects.get(username='chris')
        zuz = User.objects.get(username='zuz')
        original = Story.objects.first()
        self.assertEqual(LiteracyEvent.objects.filter(user=zuz, event_type=Event.FORKED_STORY).count(), 0)
        Story.objects.create(title="Copy", author=chris, parent=original, creation_date=now(), edit_date=now())
        self.assertEqual(LiteracyEvent.objects.filter(user=zuz, event_type=Event.FORKED_STORY).count(), 1)

    def test_story_published_event_created(self):
        chris = User.objects.get(username='chris')
        self.assertEqual(LiteracyEvent.objects.filter(user=chris, event_type=Event.PUBLISHED_STORY).count(), 1)

    def test_book_published_event_created(self):
        chris = User.objects.get(username='chris')
        zuz = User.objects.get(username='zuz')
        self.assertEqual(LiteracyEvent.objects.filter(user=chris, event_type=Event.PUBLISHED_BOOK).count(), 0)
        Book.objects.create(title="All stories", owner=zuz)
        self.assertEqual(LiteracyEvent.objects.filter(user=chris, event_type=Event.PUBLISHED_BOOK).count(), 1)
        
    def test_followed_event_created(self):
        chris = User.objects.get(username='chris')
        zuz = User.objects.get(username='zuz')
        self.assertEqual(LiteracyEvent.objects.filter(user=chris, event_type=Event.YOU_FOLLOWED).count(), 1)
        self.assertEqual(LiteracyEvent.objects.filter(user=zuz, event_type=Event.FOLLOWED).count(), 1)

        
