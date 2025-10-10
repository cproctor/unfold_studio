from django.core.management.base import BaseCommand
from text_generation.evaluation.continue_classification import ContinueClassificationModel
from tabulate import tabulate

class Command(BaseCommand):
    help="Generate labeled examples for continue function from prior story plays"

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num-examples', type=int, default=100, help="Number of examples to generate")

    def handle(self ,*args, **options):
        model = ContinueClassificationModel()
        examples = model.generate_examples(n=options['num_examples'])
        print(tabulate(examples, headers=["text", "action", "target", "label"], maxcolwidths=[60, 20, 40, None]))

