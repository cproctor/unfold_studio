from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
import math
from django.conf import settings
from commons.base.models import SoftDeleteMixin, SoftDeleteManager


class BookManager(SoftDeleteManager):
    def for_site(self, site):
        "Returns books in the current scope — associated with a site and not deleted."
        return self.filter(sites=site)

    def for_request(self, request):
        "Returns books visible to the current request"
        site = get_current_site(request)
        return self.for_site(site)


class Book(SoftDeleteMixin):
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    stories = models.ManyToManyField('unfold_studio.Story', related_name='books')
    sites = models.ManyToManyField(Site)
    priority = models.FloatField(default=0)

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
