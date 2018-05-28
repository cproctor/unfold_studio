"""
These settings are shared by all Unfold Studio deployments. 
Deployment-specific settings files should import all of these
settings and then extend or override them. 

Using the base settings as they are should get a development
instance up and running.

"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = 'http://localhost:8000'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'afg+8)$-yk((4fppx2a6@vb1$49)2)obmd6pz3ijg+r7)qy@z^'
SALT = "femqSwDDWMN"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'reversion',
    'unfold_studio',
    'profiles'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'unfold_studio.urls'

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
                'profiles.context_processors.unseen_events'
            ],
        },
    },
]

WSGI_APPLICATION = 'unfold_studio.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

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
USE_TZ = True

# Ink Directory
# Inklecate reads and write to files. INK_DIR specifies a directory which 
# should exist and have appropriate permissions.
INK_DIR = "/Users/chris/temp/inkspace"
INKLECATE = '/Users/chris/Documents/3-Software-Engineer/unfold_studio/unfold_studio/inklecate_0_6_4'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = "../static_assets"
STATIC_URL = '/static/'

# Authentication
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
AUTHENTICATION_BACKENDS = (
    #'unfold_studio.auth.TokenBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = 'login'
PASSWORD_TOKEN_MAX_AGE = 60 * 60 * 24
EMAIL_SENDER = 'unfold@chrisproctor.net'
EMAIL_SUBJECT_PREFIX = '[UNFOLD STUDIO] '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Documentation
ABOUT_STORY_ID = 30
TEACHERS_STORY_ID = 31

# Featured stories
FEATURED = {
    'FEATURED_SCORE': 10,
    'LOVE_SCORE': 1,
    'BOOK_SCORE': 1,
    'FORK_SCORE': 1,
    'GRAVITY': 1.5,
    'STORIES_TO_SHOW': 12
}
