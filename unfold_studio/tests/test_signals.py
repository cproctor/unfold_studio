from django.test import TestCase
from unfold_studio.models import Story, Book
from profiles.models import Profile, Event
from django.contrib.auth.models import User

class SignalsTestCase(TestCase):
    def setUp(self):
        chris = User.objects.create(username='chris')
        zuz = User.objects.create(username='zuz')
        Profile.objects.create(user=chris)
        Profile.objects.create(user=zuz)
        chris.profile.following.add(zuz.profile)
        s = Story.objects.create(title="My first story", author=zuz, shared=True)

    def test_loved_event_created(self):
        chris = User.objects.get(username='chris')
        zuz = User.objects.get(username='zuz')
        self.assertEqual(Event.objects.filter(user=zuz, event_type=Event.LOVED_STORY).count(), 0)
        zuz.stories.first().loves.add(chris.profile)
        self.assertEqual(Event.objects.filter(user=zuz, event_type=Event.LOVED_STORY).count(), 1)

    def test_forked_event_created(self):
        chris = User.objects.get(username='chris')
        zuz = User.objects.get(username='zuz')
        original = Story.objects.first()
        self.assertEqual(Event.objects.filter(user=zuz, event_type=Event.FORKED_STORY).count(), 0)
        Story.objects.create(title="Copy", author=chris, parent=original)
        self.assertEqual(Event.objects.filter(user=zuz, event_type=Event.FORKED_STORY).count(), 1)

    def test_story_published_event_created(self):
        chris = User.objects.get(username='chris')
        self.assertEqual(Event.objects.filter(user=chris, event_type=Event.PUBLISHED_STORY).count(), 1)

    def test_book_published_event_created(self):
        chris = User.objects.get(username='chris')
        zuz = User.objects.get(username='zuz')
        self.assertEqual(Event.objects.filter(user=chris, event_type=Event.PUBLISHED_BOOK).count(), 0)
        Book.objects.create(title="All stories", owner=zuz)
        self.assertEqual(Event.objects.filter(user=chris, event_type=Event.PUBLISHED_BOOK).count(), 1)
        
    def test_followed_event_created(self):
        chris = User.objects.get(username='chris')
        zuz = User.objects.get(username='zuz')
        self.assertEqual(Event.objects.filter(user=chris, event_type=Event.YOU_FOLLOWED).count(), 1)
        self.assertEqual(Event.objects.filter(user=zuz, event_type=Event.FOLLOWED).count(), 1)

        
