from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Make a user a teacher"

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("-r", "--remove-teacher-status", action="store_true")

    def handle(self, *args, **options):
        user = User.objects.get(username=options["username"])
        if options["remove_teacher_status"]:
            if not user.profile.is_teacher:
                raise CommandError("{} is not a teacher".format(user))
            user.profile.is_teacher = False
            user.profile.save()
        else:
            if user.profile.is_teacher:
                raise CommandError("{} is already a teacher".format(user))
            user.profile.is_teacher = True
            user.profile.save()
