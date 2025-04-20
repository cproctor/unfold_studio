import os
import sys
import django
from django.conf import settings

# Add project root and unfold_studio directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
unfold_studio_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, unfold_studio_dir)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unfold_studio.settings')

# Configure Django settings for testing
settings.configure(
    DEBUG=False,
    BASE_DIR=project_root,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.sites',
        'reversion',
        'unfold_studio',
        'text_generation',
        'generated_text_evaluator',
        'profiles',
        'literacy_groups',
        'literacy_events',
        'comments',
        'commons',
        'prompts',
    ],
    SECRET_KEY='test-key-not-for-production',
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ],
    ROOT_URLCONF='unfold_studio.urls',
    SITE_ID=1,
    TEXT_GENERATION={
        'BACKEND': 'text_generation.backends.openai.OpenAIBackend',
        'API_KEY': 'test-key',
        'MODEL': 'gpt-3.5-turbo',
        'MAX_TOKENS': 1000,
        'TEMPERATURE': 0.7,
    },
    DEFAULT_AI_SEED=42,
)

# Initialize Django
django.setup() 