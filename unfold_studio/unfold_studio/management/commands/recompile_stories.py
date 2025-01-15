from django.core.management.base import BaseCommand, CommandError
from unfold_studio.models import Story
import structlog
import reversion

log = structlog.get_logger("unfold_studio")    

class Command(BaseCommand):
    help = "Recompile all stories (for example after upgrading inklecate)"

    def handle(self, *args, **options):
        for story in Story.objects.all():
            log.debug(name="Application Alert", event="Recompiling Story", args={"story": story, "story_id": story.id})
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


