from django.core.management.base import BaseCommand
from text_generation.evaluation.continue_classification import ContinueClassificationModel
from tabulate import tabulate
import csv

class Command(BaseCommand):
    help="Generate labeled examples for continue function from prior story plays"

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num-examples', type=int, default=100, 
                help="Number of examples to generate")
        parser.add_argument('-o', "--output", help="file to save result in CSV format")

    def handle(self ,*args, **options):
        verbose = options['verbosity'] > 1
        model = ContinueClassificationModel()
        queryset = model.get_default_queryset()
        examples = model.generate_examples(
            queryset=queryset, 
            n=options['num_examples'],
            verbose=verbose
        )
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

