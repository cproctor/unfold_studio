import os
import json
from django.core.management.base import BaseCommand
from generated_text_evaluator.flows.sample_triplets_flow import SampleTripletsFlow

class Command(BaseCommand):
    """
    Examples:
        python manage.py generate_triplets --uuids abc-123 def-456 --output-filename output.json
        python manage.py generate_triplets --uuids-filename uuids.txt --output-filename output.json
    """

    help = 'Generate triplets from story play instances and save them to a JSON file'

    def add_arguments(self, parser):
        uuid_group = parser.add_mutually_exclusive_group(required=True)
        uuid_group.add_argument(
            '--uuids',
            nargs='+',
            type=str,
            help='One or more UUIDs provided directly in the command line'
        )
        uuid_group.add_argument(
            '--uuids-filename',
            type=str,
            help='Name of the file containing UUIDs (one per line), must be in the same directory as the command'
        )
        parser.add_argument(
            '--output-filename',
            type=str,
            required=True,
            help='Name of the output JSON file where triplets will be saved'
        )

    def read_uuids_from_file(self, file_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_dir, file_path)
        try:
            with open(full_path, 'r') as f:
                uuids = [line.strip() for line in f if line.strip()]
            return uuids
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Error reading UUIDs file: {str(e)}")
            )
            return []

    def get_output_filepath(self, filename):
        current_file = os.path.abspath(__file__)
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        output_dir = os.path.join(app_dir, 'triplet_samples_files')
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, filename)

    def process_story_play_instances(self, uuids):
        flow = SampleTripletsFlow()
        all_triplets = []
        
        for uuid in uuids:
            self.stdout.write(f"Processing UUID: {uuid}")
            try:
                triplets = flow.execute_flow([uuid])
                all_triplets.extend(triplets)
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Error processing UUID {uuid}: {str(e)}")
                )
        
        return all_triplets

    def save_triplets_to_file(self, triplets, filepath):
        try:
            with open(filepath, 'w') as f:
                json.dump(triplets, f, indent=2)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully saved {len(triplets)} triplets to {filepath}")
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Error saving to file: {str(e)}")
            )

    def handle(self, *args, **options):
        if options['uuids_filename']:
            uuids = self.read_uuids_from_file(options['uuids_filename'])
            if not uuids:
                return
        else:
            uuids = options['uuids']

        output_filename = options['output_filename']
        filepath = self.get_output_filepath(output_filename)
        triplets = self.process_story_play_instances(uuids)
        self.save_triplets_to_file(triplets, filepath)