import os
import django
from django.utils import timezone
from integration_tests.ci_initialization.text_generation.initialize_text_generation_records import initialize_text_generation_records

def setup_django():
    """Set up Django environment and ensure apps are ready."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unfold_studio.settings')
    django.setup()
    
    # Import Django models after setup
    from django.contrib.auth.models import User
    from django.contrib.sites.models import Site
    from unfold_studio.models import Story
    
    return User, Site, Story

def create_test_user():
    """Create a test user for integration tests."""
    User, _, _ = setup_django()
    return User.objects.create_user('testuser', 'test@example.com', 'testpass')

def get_default_site():
    """Get the default site for the application"""
    _, Site, _ = setup_django()
    return Site.objects.get(id=1)

def initialize_test_environment():
    """
    Initialize the test environment by creating necessary test data.
    This is the main entry point for test environment initialization.
    """
    # Ensure Django is set up
    setup_django()
    
    # Create test user
    user = create_test_user()
    
    # Get the default site
    site = get_default_site()
    
    # Import and call story creation functions
    from integration_tests.ci_initialization.stories.initialize_input_generate_story import create_input_generate_story
    
    # Create stories
    story_ids = []
    story_ids.append(create_input_generate_story(user, site))
    
    # Initialize text generation records
    try:
        text_gen_records = initialize_text_generation_records()
        print(f'Created {len(text_gen_records)} text generation records')
    except Exception as e:
        print(f'Failed to create text generation records: {str(e)}')
        raise
    
    print(f'Initialized test environment with {len(story_ids)} stories and {len(text_gen_records)} text generation records')
    return story_ids

if __name__ == '__main__':
    initialize_test_environment() 