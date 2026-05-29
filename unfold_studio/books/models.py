from django.db import models
from django.contrib.auth.models import User
import math
from django.conf import settings
from commons.base.models import SoftDeleteMixin, SoftDeleteManager


class BookManager(SoftDeleteManager):
    def for_request(self, request):
        return self.all()


class Book(SoftDeleteMixin):
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    stories = models.ManyToManyField('unfold_studio.Story', related_name='books')
    priority = models.FloatField(default=0)
    genres = models.JSONField(default=list, blank=True)

    objects = BookManager()

    def update_priority(self):
        self.priority = self.score()

    def score(self):
        stories = self.stories.all()
        return (1 +
            math.log(1 + len(stories)) * settings.BOOK_PRIORITY['LOG_NUM_STORIES'] +
            (stories[len(stories) // 2].priority if any(stories) else 0) *
                    settings.BOOK_PRIORITY['MEDIAN_STORY_PRIORITY']
        )

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'unfold_studio'
        ordering = ['-priority']
