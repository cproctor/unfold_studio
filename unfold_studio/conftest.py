import os
import sys
import django

# Add project root and unfold_studio directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
unfold_studio_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, unfold_studio_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unfold_studio.settings')

from django.conf import settings
settings.configure(
    DEBUG=False,
    BASE_DIR=unfold_studio_dir,
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
        'stories',
        'books',
        'story_play',
        'text_generation',
        'profiles',
        'literacy_groups',
        'literacy_events',
        'comments',
        'commons',
        'prompts',
        'research',
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
        'backend': 'OpenAI',
        'api_key': 'test-key',
        'model': 'gpt-3.5-turbo',
        'temperature': 0.7,
    },
    DEFAULT_AI_SEED=42,
    STATIC_URL='/static/',
)

django.setup()
