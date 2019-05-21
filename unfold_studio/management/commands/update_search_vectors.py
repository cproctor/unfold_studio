from django.core.management.base import BaseCommand, CommandError
from django.contrib.postgres.search import SearchVector
from unfold_studio.models import Story

class Command(BaseCommand):
    help = "Assign all extant stories to the site with the given ID"

    def handle(self, *args, **options):
        for s in Story.objects.iterator():
            s.search = SearchVector('title', 'ink')
            s.save()
