# Production settings for unfold.studio
# Overrides base_settings.py defaults with deployment-specific values.
import os
from unfold_studio.base_settings import *

BASE_URL = 'https://unfold.studio'

# In production the SECRET_KEY must always come from the environment.
SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False
ALLOWED_HOSTS = ['unfold.studio']

# Production apps: drop debug_toolbar and silk (dev-only); add production apps.
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in ('debug_toolbar', 'silk')]
INSTALLED_APPS += ['research']

# Production middleware: drop DebugToolbarMiddleware.
MIDDLEWARE = [m for m in MIDDLEWARE if m != 'debug_toolbar.middleware.DebugToolbarMiddleware']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "unfold_studio",
        "USER": "unfold_studio_user",
    }
}

# Ink compiler — paths resolved at deploy time by scripts/install_inklecate.sh.
from pathlib import Path
INK_VERSION = "1.2.0"
INK_DIR = Path(BASE_DIR).parent / "ink"
INKLECATE = Path(BASE_DIR).parent / f"inklecate_{INK_VERSION}" / "inklecate"

# Static files served from S3.
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'static.unfold.studio'
STATIC_URL = "https://static.unfold.studio/"
AWS_DEFAULT_ACL = None

AUTHENTICATION_BACKENDS = (
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

TEXT_GENERATION = {
    "backend": "OpenAI",
    "api_key": os.environ['OPENAI_API_KEY'],
    "temperature": 1.0,
    "model": "gpt-4o",
}
