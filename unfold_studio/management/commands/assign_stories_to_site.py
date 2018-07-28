from django.core.management.base import BaseCommand, CommandError
from unfold_studio.models import Story
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = "Assign all extant stories to the site with the given ID"

    def add_arguments(self, parser):
        parser.add_argument("site_id", type=int)

    def handle(self, *args, **options):
        site = Site.objects.get(pk=options['site_id'])
        for story in Story.objects.all():
            story.sites.add(site)
