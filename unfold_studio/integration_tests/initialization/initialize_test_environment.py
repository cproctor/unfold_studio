import os
import django
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

# Set up Django environment first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unfold_studio.settings')
django.setup()

def create_test_user():
    """Create a test user for integration tests."""
    return User.objects.create_user('testuser', 'test@example.com', 'testpass')

def get_default_site():
    """Get the default site for the application."""
    return Site.objects.get(id=1)

def initialize_test_environment():
    """
    Initialize the test environment by creating necessary test data.
    This is the main entry point for test environment initialization.
    """
    # Create test user
    user = create_test_user()
    
    # Get the default site
    site = get_default_site()
    
    # Import and call story creation functions
    from .stories.input_generate_story import create_input_generate_story
    
    # Create stories
    story_ids = []
    story_ids.append(create_input_generate_story(user, site))
    
    print(f'Initialized test environment with {len(story_ids)} stories')
    return story_ids

if __name__ == '__main__':
    initialize_test_environment() 