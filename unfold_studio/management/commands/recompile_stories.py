from django.core.management.base import BaseCommand, CommandError
from unfold_studio.models import Story

class Command(BaseCommand):
    help = "Recompile all stories (for example after upgrading inklecate)"

    def handle(self, *args, **options):
        for story in Story.objects.all():
            print("Recompiling '{}' (Story {})".format(story, story.id))
            story.compile_ink()
            story.save()


