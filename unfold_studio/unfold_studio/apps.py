import os
from django.conf import settings
from django.apps import AppConfig

class UnfoldStudioConfig(AppConfig):
    name = "unfold_studio"
    verbose_name = "Unfold Studio"
    path = os.path.join(settings.BASE_DIR, "unfold_studio")
