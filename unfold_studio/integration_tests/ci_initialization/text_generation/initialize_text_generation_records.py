import os
import django

# Set up Django environment first if not already set up
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unfold_studio.settings')
    django.setup()

from django.utils import timezone
from unfold_studio.models import TextGenerationRecord

def initialize_text_generation_records():
    """Initialize test records in the TextGenerationRecord model."""
    test_records = [
        {
            'prompt': 'Generate a fun fact about pizza',
            'response': 'The world\'s largest pizza was made in Rome, Italy, in 2012, measuring 13,580 square feet!',
            'record_type': 'fact',
            'timestamp': timezone.now()
        },
        {
            'prompt': 'Write a short story about blue',
            'response': 'In a world of endless skies, the color blue danced through clouds like a gentle whisper, touching everything with its serene beauty.',
            'record_type': 'story',
            'timestamp': timezone.now()
        },
        {
            'prompt': 'Create a poem about the number 7',
            'response': 'Lucky seven, standing tall\nMagic number heard in call\nSeven days to make a week\nSeven colors rainbows seek',
            'record_type': 'poem',
            'timestamp': timezone.now()
        },
        {
            'prompt': 'Make a plan for eating sushi',
            'response': '1. Start with lighter fish\n2. Use wasabi sparingly\n3. Dip fish-side down\n4. Eat in one bite\n5. Cleanse palate with ginger',
            'record_type': 'plan',
            'timestamp': timezone.now()
        },
        {
            'prompt': 'Generate a quote about red',
            'response': '"Red is the color of passion, of love, and of the fire that burns within our hearts to achieve greatness."',
            'record_type': 'quote',
            'timestamp': timezone.now()
        }
    ]

    # Clear existing test records
    TextGenerationRecord.objects.all().delete()

    # Create new records
    created_records = []
    for record in test_records:
        created_record = TextGenerationRecord.objects.create(**record)
        created_records.append(created_record)
        print(f"Created {record['record_type']} record with ID: {created_record.id}")

    return created_records 