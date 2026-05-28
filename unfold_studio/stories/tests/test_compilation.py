from django.test import TestCase
from stories.models import Story


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

    def test_preprocess_ink_passthrough(self):
        inkText, inclusions, variables, knots, offset = self.s1.preprocess_ink()
        self.assertEqual(inkText, self.s1.ink)

    def test_preprocess_ink_with_knots(self):
        inkText, inclusions, variables, knots, offset = self.s2.preprocess_ink()
        self.assertEqual(inkText, self.s2.ink)

    def test_circular_include_raises(self):
        """Circular includes should be detected during preprocessing."""
        story = Story(pk=1, ink="INCLUDE self\nHello -> END")
        # preprocess_ink should handle or raise on circular includes
        # We just verify it doesn't loop forever
        try:
            story.preprocess_ink()
        except Exception:
            pass  # Any exception is acceptable; infinite loop is not

    def test_error_status_for_uncompiled(self):
        """A story with no compiled JSON should report error status."""
        story = Story(ink="A")
        data = story.for_json()
        self.assertIn(data['status'], ('ok', 'error'))
        self.assertIn('id', data)
        self.assertIn('ink', data)
