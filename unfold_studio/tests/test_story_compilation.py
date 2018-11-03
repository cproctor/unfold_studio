from django.test import TestCase
from unfold_studio.models import Story, Book
from profiles.models import Profile, Event
from django.contrib.auth.models import User

class StoryCompilationTestCase(TestCase):
    def setUp(self):
        self.s = Story(ink="A")

    def test_get_knots_without_preamble(self):
        self.assertEqual(len(self.s.get_knots(False)), 0)

    def test_compiled_ink(self):
        inkText, inclusions, variables, knots, offset = self.s.preprocess_ink()
        self.assertEqual(inkText, "A")
