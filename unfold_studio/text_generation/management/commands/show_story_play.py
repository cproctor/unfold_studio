from django.core.management.base import BaseCommand
from story_play.models import StoryPlayInstance
from tabulate import tabulate

class Command(BaseCommand):
    help="Show the records in a StoryPlayInstance"
    def add_arguments(self, parser):
        parser.add_argument("uuid")

    def handle(self, *args, **options):
        spi = StoryPlayInstance.objects.get(uuid=options['uuid'])
        print(f"Story: {spi.story.title} ({spi.story.id})")
        timeline = [(r.story_point, r.data_type, r.data) for r in spi.records.all()]
        print(tabulate(timeline, headers=["index", "type", "data"], maxcolwidths=[None, None, 60]))



