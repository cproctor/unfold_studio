import os
import json
from typing import List, Dict, Any
from text_generation.views import GetNextDirectionView

class EvaluateGeneratedTriplets:
    def __init__(self):
        self.view = GetNextDirectionView()
        self.seed = 0  # Fixed seed for reproducibility
        
        # Create predicted_triplet_files directory if it doesn't exist
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.predicted_dir = os.path.join(os.path.dirname(current_dir), 'predicted_triplet_files')
        os.makedirs(self.predicted_dir, exist_ok=True)

    def evaluate_triplets(self, input_filename: str, output_filename: str) -> None:
        """
        Evaluate triplets from a JSON file and save predictions to a new file.
        
        Args:
            input_filename: Name of the input JSON file in triplet_samples_files directory
            output_filename: Name of the output JSON file to save in predicted_triplet_files directory
        """
        # Read input file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        input_path = os.path.join(os.path.dirname(current_dir), 'triplet_samples_files', input_filename)
        
        with open(input_path, 'r') as f:
            triplets = json.load(f)
        
        # Process each triplet
        for triplet in triplets:
            # Prepare target_knot_data
            target_knot_data = {
                'knotContents': [triplet['next_text']]
            }
            
            # Get prediction
            direction, content = self.view.get_next_direction_details_for_story(
                target_knot_data=target_knot_data,
                story_history=triplet['initial_text'],
                user_input=triplet['chosen_choice'],
                seed=self.seed
            )
            
            # Add prediction to triplet
            triplet['get_next_direction_prediction'] = {
                'direction': direction,
                'content': content
            }
        
        # Save results
        output_path = os.path.join(self.predicted_dir, output_filename)
        with open(output_path, 'w') as f:
            json.dump(triplets, f, indent=2)
        
        print(f"Processed {len(triplets)} triplets")
        print(f"Results saved to {output_path}") 