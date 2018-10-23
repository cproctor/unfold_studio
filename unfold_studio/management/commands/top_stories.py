from django.core.management.base import BaseCommand, CommandError
from unfold_studio.models import Story
from tabulate import tabulate
import csv

class Command(BaseCommand):
    help = "Show a table of top stories"

    def add_arguments(self, parser):
        parser.add_argument("-n", '--number_of_stories', type=int, default=20)
        parser.add_argument("-i", '--integers', action='store_true')
        parser.add_argument("-l", '--long_headers', action='store_true')
        parser.add_argument("-o", '--outfile')

    def handle(self, *args, **options):
        props = lambda s: (s.id, s.title, s.priority, s.age_in_hours(), s.loves.count(),  
            s.books.count(), s.children.count(), s.includes.count(),
            s.included_by.count(), int(s.errors.exists()), int(s.featured))
        zerosToDots = lambda v: '.' if v == 0 else v
        stories = map(props, Story.objects.all()[:options['number_of_stories']])
        if not options['integers']:
            stories = map(lambda story: [zerosToDots(s) for s in story], stories)
        stories = list(stories)
        if options['long_headers']:
            headers = [
                "id", "title", "priority", "age_hours", "loves", "books", "children", "includes",
                "included_by", "errors", "featured"
            ]
        else:
            headers = [
                "id", "title", "pri", "age", "<3", "bks", "chld", "inc",
                "inc_by", "err", "ftd"
            ]
        if options['outfile']:
            with open(options['outfile'], 'w') as o:
                writer = csv.writer(o)
                writer.writerow(headers)
                writer.writerows(stories)
        print(tabulate(stories, headers))
            

