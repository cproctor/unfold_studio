from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from stories.models import Story


class Command(BaseCommand):
    help = (
        "Hard-deletes public (anonymous) stories older than PUBLIC_STORY_MAX_AGE_DAYS days. "
        "Public stories are ephemeral by design and not subject to soft-delete."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Override the PUBLIC_STORY_MAX_AGE_DAYS setting for this run.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be deleted without deleting.",
        )

    def handle(self, *args, **options):
        max_age_days = options["days"] or getattr(settings, "PUBLIC_STORY_MAX_AGE_DAYS", 30)
        cutoff = timezone.now() - timedelta(days=max_age_days)

        qs = Story.all_objects.filter(
            public=True,
            author__isnull=True,
            edit_date__lt=cutoff,
        )
        count = qs.count()

        if options["dry_run"]:
            self.stdout.write(
                f"Dry run: {count} public story/stories older than {max_age_days} days would be deleted."
            )
            return

        qs.delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {count} public story/stories older than {max_age_days} days.")
        )
