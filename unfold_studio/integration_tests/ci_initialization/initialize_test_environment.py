import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unfold_studio.settings')
django.setup()

from django.contrib.auth.models import User

from unfold_studio.integration_tests.ci_initialization.text_generation.initialize_text_generation_records import initialize_text_generation_records
from unfold_studio.integration_tests.ci_initialization.text_generation.initialize_text_generation_records_for_continue import initialize_text_generation_records_for_continue
from unfold_studio.integration_tests.ci_initialization.stories.initialize_input_generate_story import create_input_generate_story
from unfold_studio.integration_tests.ci_initialization.stories.initialize_input_generate_story2 import create_input_generate_story2
from unfold_studio.integration_tests.ci_initialization.stories.initialize_input_generate_story3 import create_input_generate_story3
from unfold_studio.integration_tests.ci_initialization.stories.initialize_continue_story import create_continue_story

def create_test_user():
    try:
        return User.objects.get(username='testuser4')
    except User.DoesNotExist:
        return User.objects.create_user('testuser4', 'test@example.com', 'testpass')

def initialize_test_environment():
    print("Initializing test environment...")

    user = create_test_user()

    create_input_generate_story(user)
    create_input_generate_story2(user)
    create_input_generate_story3(user)
    create_continue_story(user)

    initialize_text_generation_records()
    initialize_text_generation_records_for_continue()

    print("Test environment initialized successfully")

if __name__ == '__main__':
    initialize_test_environment()
