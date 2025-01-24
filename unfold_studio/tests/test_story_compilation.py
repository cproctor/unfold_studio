from django.test import TestCase
from unfold_studio.models import Story, Book
from profiles.models import Profile
from django.contrib.auth.models import User

class StoryCompilationTestCase(TestCase):
    def setUp(self):
        self.s1 = Story(ink="A")
        self.s2 = Story(ink="A\n=== B ===\nB -> END")

    def test_get_preamble(self):
        self.assertEqual(self.s1.get_ink_preamble(), 'A')
        self.assertEqual(self.s2.get_ink_preamble(), 'A')

    def test_get_knots_without_preamble(self):
        self.assertEqual(len(self.s1.get_knots(False)), 0)
        self.assertEqual(len(self.s2.get_knots(False)), 1)

    def test_compiled_ink(self):
        inkText, inclusions, variables, knots, offset = self.s1.preprocess_ink()
        self.assertEqual(inkText, self.s1.ink)
        inkText, inclusions, variables, knots, offset = self.s2.preprocess_ink()
        self.assertEqual(inkText, self.s2.ink)
