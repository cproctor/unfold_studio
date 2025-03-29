import os
import random
from typing import List, Dict, Any
from generated_text_evaluator.constants import TripletType
from generated_text_evaluator.services.unfold_studio import UnfoldStudioService
from sentence_transformers import SentenceTransformer
import numpy as np

class GenerateTripletsFlow:
    
    def __init__(self):
        self.needs_input_range = 5  # Maximum number of texts to collect
        self.needs_input_difference_threshold = 2  # Number of texts to skip
        self.invalid_input_range = 5  # Maximum number of texts to collect for invalid inputs
        self.invalid_input_difference_threshold = 2  # Number of texts to skip for invalid inputs
        self.invalid_input_matching_score_threshold = 0.3  # Threshold below which we consider the action invalid
        self.invalid_input_max_attempts_per_triplet = 5    # Maximum attempts to generate an invalid action
        
        # Load actions from file during initialization
        current_dir = os.path.dirname(os.path.abspath(__file__))
        actions_file = os.path.join(current_dir, 'actions.txt')
        with open(actions_file, 'r') as f:
            self.actions = [line.strip() for line in f if line.strip()]
            
        # Initialize the sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def execute_flow(self, story_play_instance_uuids):
        triplets = []
        for story_play_instance_uuid in story_play_instance_uuids:
            try:
                instance = UnfoldStudioService.get_story_play_instance(story_play_instance_uuid)
                records = UnfoldStudioService.get_ordered_records(instance)

                direct_continue_triplets = self.get_direct_continue_triplets(records)
                triplets.extend(direct_continue_triplets)

                bridge_and_continue_triplets = self.get_bridge_and_continue_triplets(records)
                triplets.extend(bridge_and_continue_triplets)

                needs_input_triplets = self.get_needs_input_triplets(records)
                triplets.extend(needs_input_triplets)

                invalid_user_input_triplets = self.get_invalid_user_input_triplets(records)
                triplets.extend(invalid_user_input_triplets)

            except Exception as e:
                print(str(e))
                continue

        return triplets
    
    def get_direct_continue_triplets(self, records):
        triplets = []
        i = 0
        while i <= len(records) - 5:
            if UnfoldStudioService.is_valid_record_sequence_for_direct_continue(records, i):
                triplet = {
                    'initial_text': records[i].data['text'],
                    'chosen_choice': records[i+2].data,
                    'next_text': records[i+4].data['text'],
                    'triplet_type': TripletType.DIRECT_CONTINUE,
                }
                triplets.append(triplet)
                i += 3
            else:
                i += 1
        return triplets
    
    def get_bridge_and_continue_triplets(self, records):
        triplets = []
        i = 0
        while i <= len(records) - 6:
            if UnfoldStudioService.is_valid_record_sequence_for_bridge_and_continue(records, i):
                triplet = {
                    'initial_text': records[i].data['text'],
                    'chosen_choice': records[i+2].data,
                    'next_text': records[i+5].data['text'],
                    'triplet_type': TripletType.BRIDGE_AND_CONTINUE,
                }
                triplets.append(triplet)
                i += 4
            else:
                i += 1
        return triplets
    

    def get_needs_input_triplets(self, records):
        triplets = []
        i = 0
        while i <= len(records) - 4:
            if UnfoldStudioService.is_valid_record_sequence_for_needs_input(records, i):
                authors_texts = []
                j = i + 4
                skipped_authors_text = 0
                while j < len(records) and len(authors_texts) < self.needs_input_range:
                    if UnfoldStudioService.is_authors_text(records[j]):
                        if skipped_authors_text < self.needs_input_difference_threshold:
                            skipped_authors_text += 1
                        else:
                            authors_texts.append(records[j])
                    j += 1

                for text_record in authors_texts:
                    triplets.append({
                        'initial_text': records[i].data['text'],
                        'chosen_choice': records[i+2].data,
                        'next_text': text_record.data['text'],
                        'triplet_type': TripletType.NEEDS_INPUT,
                    })
                i = j
            else:
                i += 1
        return triplets
    

    def generate_random_action(self) -> str:
        return random.choice(self.actions)

    def calculate_matching_score(self, initial_text: str, chosen_choice: str, next_text: str) -> float:
        # Create the context by combining initial and next text
        context = f"{initial_text} {next_text}"
        
        # Get embeddings for context and chosen choice and move to CPU
        context_embedding = self.model.encode(context, convert_to_tensor=True).cpu()
        choice_embedding = self.model.encode(chosen_choice, convert_to_tensor=True).cpu()
        
        # Calculate cosine similarity between context and choice
        similarity = np.dot(context_embedding, choice_embedding) / (
            np.linalg.norm(context_embedding) * np.linalg.norm(choice_embedding)
        )
        
        # Convert to float and ensure it's between 0 and 1
        score = float(similarity)
        return max(0.0, min(1.0, score))

    def get_invalid_user_input_triplets(self, records):
        triplets = []
        i = 0
        while i <= len(records) - 4:
            if UnfoldStudioService.is_valid_record_sequence_for_invalid_input(records, i):
                authors_texts = []
                j = i + 4
                skipped_authors_text = 0
                while j < len(records) and len(authors_texts) < self.invalid_input_range:
                    if UnfoldStudioService.is_authors_text(records[j]):
                        if skipped_authors_text < self.invalid_input_difference_threshold:
                            skipped_authors_text += 1
                        else:
                            authors_texts.append(records[j])
                    j += 1

                initial_text = records[i].data['text']
                
                for text_record in authors_texts:
                    next_text = text_record.data['text']
                    
                    for _ in range(self.invalid_input_max_attempts_per_triplet):
                        random_action = self.generate_random_action()
                        matching_score = self.calculate_matching_score(
                            initial_text=initial_text,
                            chosen_choice=random_action,
                            next_text=next_text
                        )
                        
                        if matching_score < self.invalid_input_matching_score_threshold:
                            triplets.append({
                                'initial_text': initial_text,
                                'chosen_choice': random_action,
                                'next_text': next_text,
                                'triplet_type': TripletType.INVALID_USER_INPUT,
                                'matching_score': matching_score
                            })
                            break
                
                i = j
            else:
                i += 1
        return triplets