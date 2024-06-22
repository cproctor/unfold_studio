from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.conf import settings

template = """
Created a development site with domain {domain}.
Ensure that /etc/hosts has the following line:

    127.0.0.1   {domain}

Make sure that settings.py has the following setting:

    SITE_ID = {site.id}
"""

class Command(BaseCommand):
    help = "Populate the database with initial values for development"

    def add_arguments(self, parser):
        parser.add_argument("-d", '--domain', default="local.unfoldstudio.net")
        parser.add_argument("-n", '--name', default="Dev Unfold Studio")
        parser.add_argument("-f", '--force', action="store_true")

    def handle(self, *args, **options):
        Site.objects.all().delete()
        site = Site.objects.create(
            id=1, 
            domain=options['domain'],
            name=options['name'],
        )
        if getattr(settings, 'SITE_ID') != site.id:
            print({"site": site, **options})
            print(template.format(site=site, **options))

    User.objects.all().delete()
    usernames = ["teacher", "alicia", "ben", "chris"]
    for username in usernames:
        u = User(username=username)
        u.set_password(username)
        u.save()
