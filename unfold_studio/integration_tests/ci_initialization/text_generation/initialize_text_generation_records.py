import hashlib
import json
from text_generation.models import TextGenerationRecord
from integration_tests.constants import (
    DEFAULT_GENERATE_RESPONSE_TEXT, 
    DEFAULT_SEED, DEFAULT_BACKEND_CONFIG, 
    GENERATE_RESPONSE_TEXT_1, 
    GENERATE_RESPONSE_TEXT_2, 
    GENERATE_RESPONSE_TEXT_3, 
    GENERATE_RESPONSE_TEXT_4, 
    GENERATE_RESPONSE_TEXT_5, 
    GENERATE_RESPONSE_TEXT_6, 
    GENERATE_RESPONSE_TEXT_7, 
    GENERATE_RESPONSE_TEXT_8
)

def initialize_text_generation_records():
    print("Creating text generation records...")
    
    test_records = [

        # Text generation for all paths for story 29
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short greeting for Asif1"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short greeting for Asif2"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short greeting for Asif3"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short greeting for Asif4"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short greeting for Asif5"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short description about why he might like pizza in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short description about why he might like sushi in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short description about why he might like tacos in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short description about why he might like pasta in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short description about why he might like burger in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short poem about the color blue in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short poem about the color red in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short story about the number 7 in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short story about the number 3 in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },



        # Text generation for all paths for story 31


        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a fun fact about being 25 years old in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a fun fact about being 30 years old in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a fun fact about being 20 years old in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a fun fact about being 35 years old in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a fun fact about being 28 years old in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short story about someone who loves painting in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short poem about painting in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short story about someone who loves gaming in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short poem about gaming in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a 3-step plan to achieve the dream of becoming an astronaut in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a motivational quote about pursuing the dream of becoming an astronaut in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a 3-step plan to achieve the dream of opening a cafe in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a motivational quote about pursuing the dream of opening a cafe in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a farewell message for Alice who is 25 years old in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a farewell message for Bob who is 30 years old in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a farewell message for Charlie who is 20 years old in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a farewell message for Diana who is 35 years old in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a farewell message for Eve who is 28 years old in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': DEFAULT_GENERATE_RESPONSE_TEXT
        },

        # Text generation for all paths for story 45



        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short greeting for Asif in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': GENERATE_RESPONSE_TEXT_1
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Generate a random food suggestion"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': GENERATE_RESPONSE_TEXT_2
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short poem about the color: blue in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': GENERATE_RESPONSE_TEXT_3
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a fun fact about the number 7 in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': GENERATE_RESPONSE_TEXT_4
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Generate a random adjective"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': GENERATE_RESPONSE_TEXT_5
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Generate a random noun"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': GENERATE_RESPONSE_TEXT_6
        },
        {
            'seed': DEFAULT_SEED,
            'messages': [
                {"role": "user", "content": "Write a short story in 20 words combining summer season and sunny weather in 20 words"}
            ],
            'backend_config': DEFAULT_BACKEND_CONFIG,
            'result': GENERATE_RESPONSE_TEXT_7
        },


    ]

    created_records = []
    try:
        for i, record in enumerate(test_records, 1):
            messages_json = json.dumps(record['messages'], sort_keys=True)
            messages_str = ''.join(messages_json.split())
            
            backend_config_json = json.dumps(record['backend_config'], sort_keys=True)
            config_str = ''.join(backend_config_json.split())
            
            messages_hash = hashlib.sha256(messages_str.encode()).hexdigest()
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
        
        print(f"Successfully created {len(created_records)} text generation records")
    except Exception as e:
        print(f"Error: Failed to create text generation records: {str(e)}")
        raise

    return created_records 