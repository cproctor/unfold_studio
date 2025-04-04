import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unfold_studio.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from integration_tests.ci_initialization.text_generation.initialize_text_generation_records import initialize_text_generation_records
from integration_tests.ci_initialization.stories.initialize_input_generate_story import create_input_generate_story

def create_test_user():
    return User.objects.create_user('testuser', 'test@example.com', 'testpass')

def get_default_site():
    return Site.objects.get(id=1)

def initialize_test_environment():
    user = create_test_user()
    site = get_default_site()
    
    create_input_generate_story(user, site)
    initialize_text_generation_records()
    

if __name__ == '__main__':
    initialize_test_environment() 