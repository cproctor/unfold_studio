from django.core.management.base import BaseCommand
from text_generation.evaluation.continue_classification import ContinueClassificationModel
from tabulate import tabulate
import csv

class Command(BaseCommand):
    help="Generate labeled examples for continue function from prior story plays"

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num-examples', type=int, default=100, 
                help="Number of examples to generate")
        parser.add_argument('-s', "--story", type=int, nargs='+', 
                help="id(s) of stories to use for examples")
        parser.add_argument('-t', '--num-turn-sequences-per-story', type=int, default=0, 
                help="Max number of story plays to generate per story")
        parser.add_argument('-u', '--num-stories', type=int, default=0, 
                help="Number of stories to use in queryset")
        parser.add_argument('-o', "--output", help="file to save result in CSV format")

    def handle(self ,*args, **options):
        verbose = options['verbosity'] > 1
        model = ContinueClassificationModel()
        queryset = model.get_default_queryset()
        if options['story']:
            queryset = queryset.filter(id__in=options['story'])
        if options['num_stories']:
            queryset = queryset.order_by("?")[:options['num_stories']]
        examples = model.generate_examples(n=options['num_examples'], queryset=queryset, 
                turn_sequences_per_story=options['num_turn_sequences_per_story'], verbose=verbose)
        if options['output']:
            with open(options['output'], 'w') as fh:
                writer = csv.writer(fh)
                writer.writerows(examples)
        else:
            print(
                tabulate(
                    examples, 
                    headers=["text", "action", "target", "label"], 
                    maxcolwidths=[60, 20, 40, None]
                )
            )

