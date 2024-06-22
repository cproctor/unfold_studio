from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

def documentation_urls(request):
    return {
        'DOCUMENTATION_URL': settings.DOCUMENTATION_URL,
        'HELP_URL': settings.HELP_URL,
        'TEACHING_URL': settings.TEACHING_URL,
        'DEBUG': settings.DEBUG,
        'STATIC_URL': settings.STATIC_URL,
        'SITE': get_current_site(request),
    }
