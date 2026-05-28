from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = (
        "Removes all personal data for a user and deletes their account. "
        "Soft-deletes authored content (stories, books, groups, prompts). "
        "LiteracyEvents are preserved anonymously (subject set to NULL by FK cascade) "
        "for research integrity."
    )

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int, help="Primary key of the User to delete.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be deleted without deleting.",
        )

    def handle(self, *args, **options):
        user_id = options["user_id"]
        dry_run = options["dry_run"]

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise CommandError(f"User with id={user_id} not found.")

        # Import here to avoid circular imports at module load
        from unfold_studio.models import Story, Book
        from literacy_groups.models import LiteracyGroup
        from prompts.models import Prompt

        stories = Story.all_objects.filter(author=user)
        books = Book.all_objects.filter(owner=user)
        groups_leading = LiteracyGroup.all_objects.filter(leaders=user)
        prompts = Prompt.all_objects.filter(author=user)

        self.stdout.write(
            f"User: {user.username} (id={user.pk})\n"
            f"  Stories to soft-delete: {stories.count()}\n"
            f"  Books to soft-delete: {books.count()}\n"
            f"  Groups leading to soft-delete: {groups_leading.count()}\n"
            f"  Prompts to soft-delete: {prompts.count()}\n"
            f"  LiteracyEvents: subject FK will be set to NULL (events preserved)\n"
            f"  Profile and User records: hard-deleted\n"
        )

        if dry_run:
            self.stdout.write("Dry run — no changes made.")
            return

        with transaction.atomic():
            # Soft-delete authored content
            from django.utils import timezone
            now = timezone.now()
            stories.update(deleted=True, deleted_at=now)
            books.update(deleted=True, deleted_at=now)
            groups_leading.update(deleted=True, deleted_at=now)
            prompts.update(deleted=True, deleted_at=now)

            # Remove group memberships
            user.literacy_groups.clear()

            # Delete profile (personal data)
            if hasattr(user, 'profile'):
                user.profile.delete()

            # Delete the User record — Django SET_NULL cascades to LiteracyEvent.subject
            # and LiteracyEvent.object_user, preserving event records anonymously.
            user.delete()

        self.stdout.write(self.style.SUCCESS(f"User {user_id} deleted successfully."))
