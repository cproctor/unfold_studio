import hashlib
import json
from text_generation.models import TextGenerationRecord

def initialize_text_generation_records():
    print("Creating text generation records...")
    
    test_records = [
        {
            'seed': 12345,
            'messages': [
                {"role": "user", "content": "Generate a fun fact about pizza"},
                {"role": "assistant", "content": "The world's largest pizza was made in Rome, Italy, in 2012, measuring 13,580 square feet!"}
            ],
            'backend_config': {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 100
            },
            'result': "The world's largest pizza was made in Rome, Italy, in 2012, measuring 13,580 square feet!"
        },
        {
            'seed': 67890,
            'messages': [
                {"role": "user", "content": "Write a short story about blue"},
                {"role": "assistant", "content": "In a world of endless skies, the color blue danced through clouds like a gentle whisper, touching everything with its serene beauty."}
            ],
            'backend_config': {
                "model": "gpt-3.5-turbo",
                "temperature": 0.8,
                "max_tokens": 150
            },
            'result': "In a world of endless skies, the color blue danced through clouds like a gentle whisper, touching everything with its serene beauty."
        },
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
        }
    ]

    created_records = []
    try:
        for i, record in enumerate(test_records, 1):
            messages_json = json.dumps(record['messages'], sort_keys=True)
            backend_config_json = json.dumps(record['backend_config'], sort_keys=True)
            
            record['messages_hash'] = hashlib.sha256(messages_json.encode()).hexdigest()
            record['backend_config_hash'] = hashlib.sha256(backend_config_json.encode()).hexdigest()
            
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