from django.core.management.base import BaseCommand, CommandError
from unfold_studio.models import Story

class Command(BaseCommand):
    help = "Update the priority of all stories."

    def handle(self, *args, **options):
        for story in Story.objects.all():
            story.update_priority()
            story.save()

