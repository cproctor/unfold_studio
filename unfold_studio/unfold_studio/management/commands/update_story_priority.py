from django.core.management.base import BaseCommand, CommandError
from unfold_studio.models import Story

class Command(BaseCommand):
    help = "Update the priority of all stories."

    def add_arguments(self, parser):
        parser.add_argument('-n', "--number_to_update", type=int)

    def handle(self, *args, **options):
        if options['number_to_update']:
            stories = Story.objects.all()[:options['number_to_update']]
        else:
            stories = Story.objects.iterator(chunk_size=500)
        for story in stories:
            story.update_priority()
            story.save()

