from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from unfold_studio.models import Story


class Command(BaseCommand):
    help = (
        "Set shared=True on authored stories for the current site so the anonymous homepage "
        "shows Featured stories. For local demos (TA/client); does not affect anonymous "
        "session-only drafts (null author)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            help="Only stories by this user (default: every authored story on the site).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List stories that would be updated without saving.",
        )

    def handle(self, *args, **options):
        site = Site.objects.get(pk=settings.SITE_ID)
        qs = Story.objects.filter(
            sites=site,
            deleted=False,
            author__isnull=False,
        ).exclude(shared=True)
        if options["username"]:
            qs = qs.filter(author__username=options["username"])

        stories = list(qs.select_related("author").order_by("id"))
        if not stories:
            self.stdout.write(
                self.style.WARNING(
                    "No matching stories to update (already shared, or none on this site)."
                )
            )
            return

        if options["dry_run"]:
            self.stdout.write(self.style.NOTICE("Dry run — would set shared=True on:"))
            for s in stories:
                self.stdout.write(f"  [{s.id}] {s.title!r} — {s.author.username}")
            return

        count = Story.objects.filter(pk__in=[s.id for s in stories]).update(shared=True)
        self.stdout.write(
            self.style.SUCCESS(
                f"Marked {count} story/stories as shared for site {site.name!r} ({site.domain})."
            )
        )
        self.stdout.write(
            "Demo: log out (or use a private window) and open the site root — "
            "Featured stories should list these titles."
        )
