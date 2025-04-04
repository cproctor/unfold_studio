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
            'seed': 11111,
            'messages': [
                {"role": "user", "content": "Create a poem about the number 7"},
                {"role": "assistant", "content": "Lucky seven, standing tall\nMagic number heard in call\nSeven days to make a week\nSeven colors rainbows seek"}
            ],
            'backend_config': {
                "model": "gpt-3.5-turbo",
                "temperature": 0.9,
                "max_tokens": 100
            },
            'result': "Lucky seven, standing tall\nMagic number heard in call\nSeven days to make a week\nSeven colors rainbows seek"
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
        
        print(f"Successfully created {len(created_records)} text generation records")
    except Exception as e:
        print(f"Error: Failed to create text generation records: {str(e)}")
        raise

    return created_records 