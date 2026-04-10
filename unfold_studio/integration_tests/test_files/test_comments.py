from django.test import TestCase
from django.contrib.auth.models import User
from comments.models import Comment
from unfold_studio.models import Story
from django.utils.timezone import now

class CommentVisibilityTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user('author', password='pw')
        self.follower = User.objects.create_user('follower', password='pw')
        self.stranger = User.objects.create_user('stranger', password='pw')
        self.author.profile.following.add(self.follower.profile)  # adjust to your profile structure
        self.story = Story.objects.create(
            author=self.author,
            title="Test Story",
            ink="",
            creation_date=now(),
            edit_date=now(),
        )
        Comment.objects.create(author=self.follower, story=self.story, message="hello")

    def test_stranger_cannot_see_comments(self):
        comments = Comment.objects.for_story(self.story, viewer=self.stranger)
        self.assertEqual(comments.count(), 0)

    def test_author_can_see_comments(self):
        comments = Comment.objects.for_story(self.story, viewer=self.author)
        self.assertEqual(comments.count(), 1)

    def test_soft_deleted_comment_not_visible(self):
        Comment.objects.filter(story=self.story).update(deleted=True)
        comments = Comment.objects.for_story(self.story, viewer=self.author)
        self.assertEqual(comments.count(), 0)