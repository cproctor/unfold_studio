from django.core.management.base import BaseCommand, CommandError
from unfold_studio.models import Story
import logging
import reversion

log = logging.getLogger(__name__)    

class Command(BaseCommand):
    help = "Recompile all stories (for example after upgrading inklecate)"

    def handle(self, *args, **options):
        for story in Story.objects.all():
            log.debug("Recompiling '{}' (Story {})".format(story, story.id))
            if not story.latest_version():
                with reversion.create_revision():
                    story.save()
                    reversion.set_user(story.author)
                    reversion.set_comment("Initial version created by management script")
            story.compile()
            with reversion.create_revision():
                story.save()
                reversion.set_user(story.author)
                reversion.set_comment("Story recompiled by management script")


