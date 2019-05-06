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
BASE_URL = 'http://unfold.local:8000'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'afg+8)$-yk((4fppx2a6@vb1$49)2)obmd6pz3ijg+r7)qy@z^'
SALT = "femqSwDDWMN"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Disables signals, for use during migration
DISCONNECT_SIGNALS = False

ALLOWED_HOSTS = ['unfold.local']
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
    'debug_toolbar',
    'django_extensions',
    'reversion',
    'social_django',
    'unfold_studio',
    'profiles',
    'literacy_events',
    'prompts',
    'comments'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
                'literacy_events.context_processors.unseen_events',
                'prompts.context_processors.user_prompts',
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
INKLECATE = '/Users/chris/Documents/3-Software-Engineer/unfold_studio/unfold_studio/inklecate_0_7_4'

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
    'social_core.backends.open_id.OpenIdAuth',  # for Google authentication
    'social_core.backends.google.GoogleOpenId',  # for Google authentication
    'social_core.backends.google.GoogleOAuth2',  # for Google authentication
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = 'login'
PASSWORD_TOKEN_MAX_AGE = 60 * 60 * 24
EMAIL_SENDER = 'unfold@chrisproctor.net'
EMAIL_SUBJECT_PREFIX = '[UNFOLD STUDIO] '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

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
HELP_URL = DOCUMENTATION_URL + 'user_guide/'
TEACHING_URL = DOCUMENTATION_URL + 'teaching/'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY =''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''
SOCIAL_AUTH_POSTGRES_JSONFIELD = True

SEARCH_RANK_CUTOFF = 0.01

