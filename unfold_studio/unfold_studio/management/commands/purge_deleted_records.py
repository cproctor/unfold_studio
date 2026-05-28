from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = (
        "Hard-deletes records that have been soft-deleted for longer than --days (default 90). "
        "Run manually as needed; no automatic scheduling is configured."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Purge records soft-deleted more than this many days ago (default 90).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print counts without deleting.",
        )

    def handle(self, *args, **options):
        from stories.models import Story
        from books.models import Book
        from literacy_groups.models import LiteracyGroup
        from prompts.models import Prompt

        cutoff = timezone.now() - timedelta(days=options["days"])
        dry_run = options["dry_run"]

        models = [
            ("Story", Story),
            ("Book", Book),
            ("LiteracyGroup", LiteracyGroup),
            ("Prompt", Prompt),
        ]

        total = 0
        for label, model in models:
            qs = model.all_objects.filter(deleted=True, deleted_at__lt=cutoff)
            count = qs.count()
            total += count
            if not dry_run:
                qs.delete()
            self.stdout.write(
                f"{'Would delete' if dry_run else 'Deleted'} {count} {label} record(s)."
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"{'Dry run — ' if dry_run else ''}Total: {total} record(s) {'would be ' if dry_run else ''}purged."
            )
        )
