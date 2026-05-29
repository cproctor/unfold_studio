from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Populate the database with initial values for development"

    def handle(self, *args, **options):
        User.objects.all().delete()
        usernames = ["teacher", "alicia", "ben", "chris"]
        for username in usernames:
            u = User(username=username)
            u.set_password(username)
            u.save()
        self.stdout.write(self.style.SUCCESS("Created users: " + ", ".join(usernames)))
