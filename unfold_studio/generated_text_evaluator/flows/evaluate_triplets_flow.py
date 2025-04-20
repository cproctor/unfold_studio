import json
from typing import List, Dict, Any
from text_generation.views import GetNextDirectionView
from collections import defaultdict
from generated_text_evaluator.constants import TripletType

class EvaluateGeneratedTriplets:
    def __init__(self):
        self.view = GetNextDirectionView()
        self.seed = 0  # Fixed seed for reproducibility

    def calculate_metrics(self, evaluated_triplets: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """
        Calculate metrics for each triplet type after all evaluations are complete.
        
        Args:
            evaluated_triplets: List of triplets with their predictions
            
        Returns:
            Dictionary containing metrics for each triplet type
        """
        metrics = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0})
        
        # Count true positives, false positives, and false negatives
        for triplet in evaluated_triplets:
            true_type = triplet['triplet_type']
            predicted_type = triplet['get_next_direction_prediction']['direction']
            
            if true_type == predicted_type:
                metrics[true_type]['tp'] += 1
            else:
                metrics[predicted_type]['fp'] += 1
                metrics[true_type]['fn'] += 1
        
        # Calculate precision, recall, and F1 for each type
        results = {}
        for triplet_type in TripletType.values():
            stats = metrics[triplet_type]
            precision = stats['tp'] / (stats['tp'] + stats['fp']) if (stats['tp'] + stats['fp']) > 0 else 0
            recall = stats['tp'] / (stats['tp'] + stats['fn']) if (stats['tp'] + stats['fn']) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            results[triplet_type] = {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'true_positives': stats['tp'],
                'false_positives': stats['fp'],
                'false_negatives': stats['fn']
            }
        
        return results

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
        
        # Calculate metrics after all evaluations
        metrics = self.calculate_metrics(triplets)
        
        # Print metrics
        print("\nMetrics by Triplet Type:")
        print("-" * 50)
        
        for triplet_type, type_metrics in metrics.items():
            print(f"\n{triplet_type}:")
            print(f"Precision: {type_metrics['precision']:.3f}")
            print(f"Recall: {type_metrics['recall']:.3f}")
            print(f"F1 Score: {type_metrics['f1']:.3f}")
            print(f"True Positives: {type_metrics['true_positives']}")
            print(f"False Positives: {type_metrics['false_positives']}")
            print(f"False Negatives: {type_metrics['false_negatives']}")
        
        print("-" * 50)
        
        return triplets 