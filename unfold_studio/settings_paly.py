"""
Dev computer settings file for paly stories
"""

import os
from unfold_studio.base_settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.paly.sqlite3'),
    }
}
