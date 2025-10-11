from django.core.management.base import BaseCommand
from text_generation.evaluation.continue_classification import ContinueClassificationModel
from tabulate import tabulate
import csv

class Command(BaseCommand):
    help="Evaluate labeled examples for continue function from prior story plays"

    def add_arguments(self, parser):
        parser.add_argument('examples', help="File path for examples in CSV format")

    def handle(self ,*args, **options):
        with open(options["examples"]) as fh:
            examples = list(csv.reader(fh))
        model = ContinueClassificationModel()
        model.evaluate(examples)
        model.report_evaluation_results()
