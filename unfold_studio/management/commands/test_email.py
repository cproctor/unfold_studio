from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail

class Command(BaseCommand):
    help = "Send a test email to Chris"

    def handle(self, *args, **options):
        send_mail("Test", "This is an automatically-generated test email", 
                "accounts@unfoldstudio.net", ["chris@chrisproctor.net"])
        

