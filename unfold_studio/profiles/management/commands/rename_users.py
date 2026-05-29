import csv
import sys
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from profiles.models import DeprecatedUsername


class Command(BaseCommand):
    help = (
        "Rename users from a CSV file with columns old_username,new_username. "
        "Records the old username in DeprecatedUsername so it cannot be reclaimed."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            nargs='?',
            default='-',
            help='Path to CSV file (default: stdin). Columns: old_username,new_username',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would happen without making changes.',
        )

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        dry_run = options['dry_run']

        if csv_path == '-':
            reader = csv.DictReader(sys.stdin)
        else:
            try:
                f = open(csv_path, newline='', encoding='utf-8')
                reader = csv.DictReader(f)
            except FileNotFoundError:
                raise CommandError(f'File not found: {csv_path}')

        rows = list(reader)
        if csv_path != '-':
            f.close()

        if not rows:
            self.stdout.write('No rows to process.')
            return

        errors = []
        for row in rows:
            old = row.get('old_username', '').strip()
            new = row.get('new_username', '').strip()
            if not old or not new:
                errors.append(f'Skipping row with missing values: {row!r}')
                continue
            if not User.objects.filter(username=old).exists():
                errors.append(f'User not found: {old}')
                continue
            if User.objects.filter(username=new).exists() and new != old:
                errors.append(f'Target username already taken: {new}')
                continue

        if errors:
            for e in errors:
                self.stderr.write(self.style.ERROR(e))
            raise CommandError('Aborted due to errors above. No changes made.')

        with transaction.atomic():
            for row in rows:
                old = row['old_username'].strip()
                new = row['new_username'].strip()
                if old == new:
                    self.stdout.write(f'Skipping {old} (unchanged).')
                    continue
                if dry_run:
                    self.stdout.write(f'Would rename {old} → {new}')
                    continue
                user = User.objects.get(username=old)
                user.username = new
                user.save()
                DeprecatedUsername.objects.get_or_create(
                    old_username=old,
                    defaults={'new_username': new},
                )
                self.stdout.write(self.style.SUCCESS(f'Renamed {old} → {new}'))

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run — no changes saved.'))
