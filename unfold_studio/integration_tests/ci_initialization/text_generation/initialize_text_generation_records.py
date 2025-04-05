import hashlib
import json
from text_generation.models import TextGenerationRecord

def initialize_text_generation_records():
    print("Creating text generation records...")
    
    test_records = [
        {
            'seed': 45,
            'messages': [
                {"role": "user", "content": "Write a short greeting for Asif1"}
            ],
            'backend_config': {
                "backend": "OpenAI",
                "api_key": "...",
                "temperature": 1.0,
                "model": "gpt-4o-2024-05-13",
                "memoize": False,
            },
            'result': "cached gen text yayyyyyyyy"
        },
        {
            'seed': 45,
            'messages': [
                {"role": "user", "content": "Write a short greeting for Asif2"}
            ],
            'backend_config': {
                "backend": "OpenAI",
                "api_key": "...",
                "temperature": 1.0,
                "model": "gpt-4o-2024-05-13",
                "memoize": False,
            },
            'result': "cached gen text yayyyyyyyy"
        },
        {
            'seed': 45,
            'messages': [
                {"role": "user", "content": "Write a short greeting for Asif3"}
            ],
            'backend_config': {
                "backend": "OpenAI",
                "api_key": "...",
                "temperature": 1.0,
                "model": "gpt-4o-2024-05-13",
                "memoize": False,
            },
            'result': "cached gen text yayyyyyyyy"
        },
        {
            'seed': 45,
            'messages': [
                {"role": "user", "content": "Write a short greeting for Asif4"}
            ],
            'backend_config': {
                "backend": "OpenAI",
                "api_key": "...",
                "temperature": 1.0,
                "model": "gpt-4o-2024-05-13",
                "memoize": False,
            },
            'result': "cached gen text yayyyyyyyy"
        },
        {
            'seed': 45,
            'messages': [
                {"role": "user", "content": "Write a short greeting for Asif5"}
            ],
            'backend_config': {
                "backend": "OpenAI",
                "api_key": "...",
                "temperature": 1.0,
                "model": "gpt-4o-2024-05-13",
                "memoize": False,
            },
            'result': "cached gen text yayyyyyyyy"
        },
    ]

    created_records = []
    try:
        for i, record in enumerate(test_records, 1):
            messages_json = json.dumps(record['messages'], sort_keys=True)
            messages_str = ''.join(messages_json.split())
            
            backend_config_json = json.dumps(record['backend_config'], sort_keys=True)
            config_str = ''.join(backend_config_json.split())
            
            record['messages_hash'] = hashlib.sha256(messages_str.encode()).hexdigest()
            record['backend_config_hash'] = hashlib.sha256(config_str.encode()).hexdigest()
            
            created_record = TextGenerationRecord.objects.create(**record)
            created_records.append(created_record)
            print(f"Created text generation record {i}/{len(test_records)} - ID: {created_record.id}")
            print(f"  seed: {created_record.seed}")
            print(f"  messages: {created_record.messages}")
            print(f"  messages_hash: {created_record.messages_hash}")
            print(f"  backend_config: {created_record.backend_config}")
            print(f"  backend_config_hash: {created_record.backend_config_hash}")
            print(f"  result: {created_record.result}")
        
        print(f"Successfully created {len(created_records)} text generation records")
    except Exception as e:
        print(f"Error: Failed to create text generation records: {str(e)}")
        raise

    return created_records 