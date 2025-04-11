import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unfold_studio.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from unfold_studio.integration_tests.ci_initialization.text_generation.initialize_text_generation_records import initialize_text_generation_records
from unfold_studio.integration_tests.ci_initialization.stories.initialize_input_generate_story import create_input_generate_story
from unfold_studio.integration_tests.ci_initialization.stories.initialize_input_generate_story2 import create_input_generate_story2
from unfold_studio.integration_tests.ci_initialization.stories.initialize_input_generate_story3 import create_input_generate_story3
from unfold_studio.integration_tests.ci_initialization.stories.initialize_continue_story import create_continue_story

def create_test_user():
    return User.objects.create_user('testuser', 'test@example.com', 'testpass')

def get_default_site():
    return Site.objects.get(id=1)

def initialize_test_environment():
    print("Initializing test environment...")

    user = create_test_user()
    site = get_default_site()
    
    create_input_generate_story(user, site)
    create_input_generate_story2(user, site)
    create_input_generate_story3(user, site)
    create_continue_story(user, site)

    initialize_text_generation_records()
    
    print("Test environment initialized successfully")

if __name__ == '__main__':
    initialize_test_environment() 
    