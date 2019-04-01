from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import csv

class Command(BaseCommand):
    help = "Bulk import users"

    def add_arguments(self, parser):
        parser.add_argument("csvfile")

    def handle(self, *args, **options):
        with open(options['csvfile']) as inf:
            reader = csv.DictReader(inf)
            for row in reader:
                if User.objects.filter(email=row['email']).exists():
                    print(" - {} already exists".format(row['email']))
                    continue
                u = User(
                    email=row['email'],
                    username=row['username'],
                    first_name=row['first_name'],
                    last_name=row['last_name']
                )
                u.set_password(row['password'])
                u.save()
                print(' * created account for {}'.format(row['email']))
