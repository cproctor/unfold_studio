from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Delete users who haven't logged in recently and who have no stories"

    def add_arguments(self, parser):
        parser.add_argument("-a", "--age", help="minimum age in days", default=90)
        parser.add_argument("-d", "--dryrun", help="show users who would be deleted, but don't delete them", action="store_true")

    def handle(self, *args, **options):
        verbosity = int(options["verbosity"])
        cutoff = timezone.now() - timedelta(days=int(options["age"]))
        null_users = User.objects.annotate(num_stories=Count("stories")).filter(num_stories=0, last_login__lt=cutoff)
        if verbosity > 0 or options["dryrun"]:
            self.stdout.write("{} users {} be deleted".format(null_users.count(), "would" if options["dryrun"] else "will"))
            if verbosity > 1:
                for user in null_users.all():
                    self.stdout.write(" - {}".format(user))
        if not options["dryrun"]:
            for user in null_users.all():
                user.delete()
