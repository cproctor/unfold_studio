import os
import json
from django.core.management.base import BaseCommand
from generated_text_evaluator.flows.evaluate_triplets_flow import EvaluateGeneratedTriplets
from generated_text_evaluator.constants import GENERATED_TRIPLETS_DIR, EVELUATED_TRIPLETS_DIR

class Command(BaseCommand):
    """
    Examples:
        python manage.py evaluate_triplets --input-filename input.json --output-filename output.json
    """

    help = 'Evaluate triplets from a JSON file and save predictions to a new file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input-filename',
            type=str,
            required=True,
            help=f'Name of the input JSON file in {GENERATED_TRIPLETS_DIR} directory'
        )
        parser.add_argument(
            '--output-filename',
            type=str,
            required=True,
            help=f'Name of the output JSON file to save in {EVELUATED_TRIPLETS_DIR} directory'
        )

    def get_input_filepath(self, filename):
        current_file = os.path.abspath(__file__)
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        input_dir = os.path.join(app_dir, GENERATED_TRIPLETS_DIR)
        return os.path.join(input_dir, filename)

    def get_output_filepath(self, filename):
        current_file = os.path.abspath(__file__)
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        output_dir = os.path.join(app_dir, EVELUATED_TRIPLETS_DIR)
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, filename)

    def read_triplets_from_file(self, filepath):
        try:
            with open(filepath, 'r') as f:
                triplets = json.load(f)
            return triplets
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Error reading triplets file: {str(e)}")
            )
            return []

    def save_triplets_to_file(self, triplets, filepath):
        try:
            with open(filepath, 'w') as f:
                json.dump(triplets, f, indent=2)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully saved {len(triplets)} evaluated triplets to {filepath}")
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Error saving to file: {str(e)}")
            )

    def handle(self, *args, **options):
        input_filename = options['input_filename']
        output_filename = options['output_filename']
        
        input_filepath = self.get_input_filepath(input_filename)
        output_filepath = self.get_output_filepath(output_filename)
        
        triplets = self.read_triplets_from_file(input_filepath)
        if not triplets:
            return
        
        self.stdout.write(f"Processing {len(triplets)} triplets...")
        flow = EvaluateGeneratedTriplets()
        evaluated_triplets = flow.evaluate_triplets(triplets)
        
        self.save_triplets_to_file(evaluated_triplets, output_filepath) 