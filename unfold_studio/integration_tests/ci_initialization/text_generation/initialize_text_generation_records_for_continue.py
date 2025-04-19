import hashlib
import json
from text_generation.models import TextGenerationRecord
from integration_tests.constants import (
    DEFAULT_GENERATE_RESPONSE_TEXT, 
    DEFAULT_SEED, DEFAULT_BACKEND_CONFIG, 
)

def initialize_text_generation_records_for_continue():
    print("Creating text generation records for continue...")
    
    test_records = [

        # Text generation for all story id 54
        {
            'seed': DEFAULT_SEED,
            'messages_hash': '2f173ebf039c4e422c08cedaa19fb3e0c837c2177a579e0fd9d28ff18f425c50',
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT,
            'messages': [{}]
        },
        {
            'seed': DEFAULT_SEED,
            'messages_hash': 'c7a0635a369636fc0507eebfa2345d2a8ac6cb5bfcd56e3c54b83e32683717e5',
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT,
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