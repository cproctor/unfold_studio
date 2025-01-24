from django.core.management.base import BaseCommand, CommandError
import pytz
from unfold_studio.models import Story
from literacy_events.models import LiteracyEvent

class Command(BaseCommand):
    help = "Localize all datetimes in the database as UTC"

    def handle(self, *args, **kwargs):
        tz = pytz.timezone('utc')
        for s in Story.objects.all():
            if not s.creation_date.tzinfo:
                s.creation_date = tz.localize(s.creation_date)
            if not s.edit_date.tzinfo:
                s.edit_date = tz.localize(s.edit_date)
            s.save()
        for e in LiteracyEvent.objects.all():
            if not e.timestamp.tzinfo:
                e.timestamp = tz.localize(e.timestamp)
                e.save()
