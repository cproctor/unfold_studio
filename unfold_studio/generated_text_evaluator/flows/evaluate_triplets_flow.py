import json
from typing import List, Dict, Any
from text_generation.views import GetNextDirectionView

class EvaluateGeneratedTriplets:
    def __init__(self):
        self.view = GetNextDirectionView()
        self.seed = 0  # Fixed seed for reproducibility

    def evaluate_triplets(self, triplets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate triplets and add predictions to each triplet.
        
        Args:
            triplets: List of triplets to evaluate
            
        Returns:
            List of triplets with added predictions
        """
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
        
        return triplets 