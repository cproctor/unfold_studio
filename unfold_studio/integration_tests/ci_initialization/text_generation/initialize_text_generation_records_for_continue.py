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
        {
            'seed': DEFAULT_SEED,
            'messages_hash': '7e6d0490cbc05ac1b14dfc3e4074ebd3e2baad9d06fce6e8313b437e5af2c0bf',
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
