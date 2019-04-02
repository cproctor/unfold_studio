from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
import csv

class Command(BaseCommand):
    help = "Group users based on 'username' and 'group' fields in csv"

    def add_arguments(self, parser):
        parser.add_argument("csvfile")

    def handle(self, *args, **options):
        with open(options['csvfile']) as inf:
            reader = csv.DictReader(inf)
            for row in reader:
                try:
                    user = User.objects.get(username=row['username'])
                    group, _ = Group.objects.get_or_create(name=row['group'])
                    group.user_set.add(user)
                    print(' * added {} to group {}'.format(user, group))
                except User.DoesNotExist:
                    print(" - No user with username {}".format(row['username']))
