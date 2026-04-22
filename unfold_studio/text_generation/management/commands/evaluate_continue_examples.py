from django.core.management.base import BaseCommand
from text_generation.evaluation.continue_classification import ContinueClassificationModel
from tabulate import tabulate
import csv

class Command(BaseCommand):
    help="Evaluate labeled examples for continue function from prior story plays"

    def add_arguments(self, parser):
        parser.add_argument('examples', help="File path for examples in CSV format")
        parser.add_argument('-e', "--errors", help="File path to save error analysis as CSV")
        parser.add_argument('-p', "--max-parallel-requests", type=int, default=8, 
                help="Maximum number of parallel requests for classification")
        parser.add_argument('-s', "--stats-csv", 
                help="Output stats as a CSV row, with the provided string as the version name")

    def handle(self ,*args, **options):
        with open(options["examples"]) as fh:
            examples = list(csv.reader(fh))
        model = ContinueClassificationModel()
        model.evaluate(examples, max_parallel_requests=options["max_parallel_requests"])
        if options["stats_csv"]:
            model.evaluation_stats_csv(options["stats_csv"])
        else:
            model.report_evaluation_results()
        if options["errors"]:
            if not options["stats_csv"]:
                model.report_error_analysis()
            model.save_error_analysis(options["errors"])
