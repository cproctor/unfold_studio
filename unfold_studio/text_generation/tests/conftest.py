import os
import django
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unfold_studio.settings')
settings.configure(
    DEBUG=True,
    BASE_DIR=BASE_DIR,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS = [
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
    'generated_text_evaluator'
    ],
    SITE_ID=1,
    TEXT_GENERATION={},
    DEFAULT_AI_SEED=123,
)
django.setup()
