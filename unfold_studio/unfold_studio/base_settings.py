"""
These settings are shared by all Unfold Studio deployments. 
Deployment-specific settings files should import all of these
settings and then extend or override them. 

Using the base settings as they are should get a development
instance up and running.

"""

import os
from pathlib import Path
from unfold_studio.logger import *

SITE_ID = 1

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = 'http://local.unfoldstudio.net:8000'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'afg+8)$-yk((4fppx2a6@vb1$49)2)obmd6pz3ijg+r7)qy@z^'
SALT = "femqSwDDWMN"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Disables signals, for use during migration
DISCONNECT_SIGNALS = False

ALLOWED_HOSTS = ['local.unfoldstudio.net']
INTERNAL_IPS = ['127.0.0.1']

# Application definition
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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_structlog.middlewares.RequestMiddleware",
]

if DEBUG:
    INSTALLED_APPS += ['silk']
    MIDDLEWARE += ['silk.middleware.SilkyMiddleware']

ROOT_URLCONF = 'unfold_studio.urls.base'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'literacy_events.context_processors.notifications',
                'unfold_studio.context_processors.documentation_urls',
                'social_django.context_processors.backends', 
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'unfold_studio.wsgi.application'

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "unfold_studio",
        "USER": "unfold_studio_user",
        "PASSWORD": '<password>',
        "HOST": "localhost",
        "PORT": "5432"
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True

# Ink
# Inklecate reads and write to files. INK_DIR specifies a directory which 
# should exist and have appropriate permissions.
INK_VERSION = "1.2.0"
INK_DIR = Path(BASE_DIR).parent / "ink"
INKLECATE = Path(BASE_DIR).parent / f"inklecate_{INK_VERSION}" / "inklecate"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = Path(BASE_DIR).parent / "static_assets"

STATIC_URL = '/static/'

# Authentication
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

LOGIN_URL = 'login'
PASSWORD_TOKEN_MAX_AGE = 60 * 60 * 24
EMAIL_SENDER = 'unfold@chrisproctor.net'
EMAIL_SUBJECT_PREFIX = '[UNFOLD STUDIO] '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_AI_SEED = 45
TEXT_GENERATION = {
    "backend": "OpenAI",
    "api_key": "...",
    "temperature": 1.0,
    "model": "gpt-4o-2024-05-13",
    "memoize": False,
}

# Users in the given groups will be shown the following messages on the homepage
GROUP_HOMEPAGE_MESSAGES = {}

# Featured stories
STORY_PRIORITY = {
    'FEATURED_SCORE': 10,
    'LOVE_SCORE': 5,
    'BOOK_SCORE': 1,
    'FORK_SCORE': 3,
    'INCLUDED_BY_SCORE': 1,
    'INCLUDES_SCORE': 1,
    'ERRORS_SCORE': -10,
    'GRAVITY': 1.5,
}
STORIES_ON_HOMEPAGE = 20

STORIES_PER_PAGE = 20
FEED_ITEMS_ON_PROFILE = 20
FEED_ITEMS_PER_PAGE = 40

BOOK_PRIORITY = {
    'LOG_NUM_STORIES': 1,
    'MEDIAN_STORY_PRIORITY': 10
}

DOCUMENTATION_URL = 'http://docs.unfold.studio/'
HELP_URL = DOCUMENTATION_URL + 'user_guide/index.html'
TEACHING_URL = DOCUMENTATION_URL + 'teaching/index.html'

ENABLE_ANALYTICS = True
ANALYTICS_URL = "//analytics.unfoldstudio.net/"
ANALYTICS_SITE_ID = "2"

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY =''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''
SOCIAL_AUTH_POSTGRES_JSONFIELD = True

SEARCH_RANK_CUTOFF = 0.01

CORS_ORIGIN_ALLOW_ALL = True
