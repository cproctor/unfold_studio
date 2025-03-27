import os
import django
from django.conf import settings

def pytest_configure():
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
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sites',
            'reversion',
            'unfold_studio',
            'generated_text_evaluator',
            'profiles',
            'literacy_groups',
            'literacy_events',
        ],
        SECRET_KEY='test-key-not-for-production',
        MIDDLEWARE=[],
        ROOT_URLCONF='unfold_studio.urls',
        SITE_ID=1,
    )
    django.setup() 