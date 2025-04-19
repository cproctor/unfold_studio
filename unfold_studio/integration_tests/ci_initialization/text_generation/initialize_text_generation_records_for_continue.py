import hashlib
import json
from text_generation.models import TextGenerationRecord
from integration_tests.constants import (
    DEFAULT_SEED, 
    DEFAULT_BACKEND_CONFIG, 
)

def initialize_text_generation_records_for_continue():
    print("Creating text generation records for continue...")
    
    test_records = [
        # Text generation for all story id 0
        # 1. Direct continue
        {
            'seed': DEFAULT_SEED,
            'messages_hash': "2771a5b04e1d5353438ad3feb4ca0fbb0d6c4a35e1a64309f79ffc2cce607699",
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': {
                "probabilities": {
                    "DIRECT_CONTINUE": 1.0,
                    "BRIDGE_AND_CONTINUE": 0.0,
                    "NEEDS_INPUT": 0.0,
                    "INVALID_USER_INPUT": 0.0
                },
                "direct_continue": {
                    "reason": "User input 'nothing' indicates acceptance of story conclusion without further action"
                },
                "bridge_and_continue": {
                    "reason": "Not applicable - direct continuation is sufficient",
                    "bridge_text": ""
                },
                "needs_input": {
                    "reason": "Not required - user explicitly chose no action",
                    "guidance_text": ""
                },
                "invalid_user_input": {
                    "reason": "'nothing' is a valid and meaningful input in this context"
                }
            },
            'messages': [{}]
        },
        # 2. Bridge and continue
        {
            'seed': DEFAULT_SEED,
            'messages_hash': "a422c767397fa827190715f80b91a7f0da05992c842a755a569bc15ff4850f3f",
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': {
                "probabilities": {
                    "DIRECT_CONTINUE": 0.0,
                    "BRIDGE_AND_CONTINUE": 1.0,
                    "NEEDS_INPUT": 0.0,
                    "INVALID_USER_INPUT": 0.0
                },
                "direct_continue": {
                    "reason": "The user input 'nothing' doesn't provide direct action matching the final knot conditions"
                },
                "bridge_and_continue": {
                    "reason": "A narrative bridge can naturally transition from inaction to story conclusion",
                    "bridge_text": "After following through with your input, the journey continues, leading you closer to the final destination..."
                },
                "needs_input": {
                    "reason": "The input is minimal but clear enough to proceed",
                    "guidance_text": ""
                },
                "invalid_user_input": {
                    "reason": "'nothing' is a valid response indicating passive progression"
                }
            },
            'messages': [{}]
        },
        # 3. Needs input
        {
            'seed': DEFAULT_SEED,
            'messages_hash': "e5896b0798d2bd3db2b5b8ce9564ab3055937dcd84b0b04fe4bad15606a16c8d",
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': {
                "probabilities": {
                    "DIRECT_CONTINUE": 0.0,
                    "BRIDGE_AND_CONTINUE": 0.0,
                    "NEEDS_INPUT": 1.0,
                    "INVALID_USER_INPUT": 0.0
                },
                "direct_continue": {
                    "reason": "The user input 'needs_input_input' does not directly match the final knot conditions."
                },
                "bridge_and_continue": {
                    "reason": "While a bridge could be created to lead to the final knot, the user input is too vague to create a coherent narrative bridge.",
                    "bridge_text": "..."
                },
                "needs_input": {
                    "reason": "The user input 'needs_input_input' is too vague and requires more specific actions or decisions to proceed logically.",
                    "guidance_text": "Could you please specify what action you would like to take next?"
                },
                "invalid_user_input": {
                    "reason": "The input is not completely nonsensical but lacks clarity for progressing the story."
                }
            },
            'messages': [{}]
        },
        # 4. Invalid user input
        {
            'seed': DEFAULT_SEED,
            'messages_hash': "3122cf68ee1cf9c375fc7df6e23d5c56beea44e2179fe1baa5eb510bd1c148f5",
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': {
                "probabilities": {
                    "DIRECT_CONTINUE": 0.0,
                    "BRIDGE_AND_CONTINUE": 0.0,
                    "NEEDS_INPUT": 0.0,
                    "INVALID_USER_INPUT": 1.0
                },
                "direct_continue": {
                    "reason": "User input does not provide any actionable content to continue the story directly."
                },
                "bridge_and_continue": {
                    "reason": "Transitioning is not possible because user input lacks coherence or relevance.",
                    "bridge_text": ""
                },
                "needs_input": {
                    "reason": "User input is not actionable and requires clarification to proceed.",
                    "guidance_text": ""
                },
                "invalid_user_input": {
                    "reason": "User input is gibberish, nonsensical or completely unrelated to the story context."
                }
            },
            'messages': [{}]
        },

    ]

    created_records = []
    try:
        for i, record in enumerate(test_records, 1):            
            backend_config_json = json.dumps(record['backend_config'], sort_keys=True)
            config_str = ''.join(backend_config_json.split())
            
            messages_hash = record['messages_hash']
            backend_config_hash = hashlib.sha256(config_str.encode()).hexdigest()
            
            # Check if record already exists
            existing_record = TextGenerationRecord.objects.filter(
                messages_hash=messages_hash,
                backend_config_hash=backend_config_hash,
                seed=record['seed']
            ).first()
            
            if existing_record:
                print(f"Found existing text generation record {i}/{len(test_records)} - ID: {existing_record.id}")
                created_records.append(existing_record)
            else:
                record['messages_hash'] = messages_hash
                record['backend_config_hash'] = backend_config_hash
                record['result'] = json.dumps(record['result'])
                created_record = TextGenerationRecord.objects.create(**record)
                created_records.append(created_record)
                print(f"Created new text generation record {i}/{len(test_records)} - ID: {created_record.id}")
                print(f"  seed: {created_record.seed}")
                print(f"  messages: {created_record.messages}")
                print(f"  messages_hash: {created_record.messages_hash}")
                print(f"  backend_config: {created_record.backend_config}")
                print(f"  backend_config_hash: {created_record.backend_config_hash}")
                print(f"  result: {created_record.result}")
        
        print(f"Successfully created {len(created_records)} text generation records for continue")
    except Exception as e:
        print(f"Error: Failed to create text generation records for continue: {str(e)}")
        raise

    return created_records
