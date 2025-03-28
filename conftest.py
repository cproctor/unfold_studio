import os
import sys
import django
from django.conf import settings

# Add both project root and unfold_studio directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
unfold_studio_dir = os.path.join(project_root, 'unfold_studio')
sys.path.insert(0, project_root)
sys.path.insert(0, unfold_studio_dir)

# Configure Django settings before any imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unfold_studio.settings')
settings.configure(
    DEBUG=True,
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
        'storages',
        'debug_toolbar',
        'django_extensions',
        "django_structlog",
        'reversion',
        'social_django',
        'qr_code',
        'corsheaders',
        'unfold_studio',
        'profiles',
        'literacy_events',
        'literacy_groups',
        'prompts',
        'comments',
        'text_generation',
        'generated_text_evaluator',
    ],
    SECRET_KEY='test-key-not-for-production',
    MIDDLEWARE=[],
    ROOT_URLCONF='unfold_studio.urls',
    SITE_ID=1,
    TEXT_GENERATION={},
    DEFAULT_AI_SEED=123,
)
django.setup() 