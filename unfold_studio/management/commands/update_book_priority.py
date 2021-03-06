from django.core.management.base import BaseCommand, CommandError
from unfold_studio.models import Book

class Command(BaseCommand):
    help = "Update the priority of all books."

    def handle(self, *args, **options):
        for book in Book.objects.iterator(chunk_size=500):
            book.update_priority()
            book.save()


