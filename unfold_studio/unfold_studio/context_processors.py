from django.conf import settings

def documentation_urls(request):
    return {
        'DOCUMENTATION_URL': settings.DOCUMENTATION_URL,
        'HELP_URL': settings.HELP_URL,
        'TEACHING_URL': settings.TEACHING_URL,
        'DOCS_URLS': getattr(settings, 'DOCS_URLS', {}),
        'DEBUG': settings.DEBUG,
        'STATIC_URL': settings.STATIC_URL,
        'SITE_NAME': settings.SITE_NAME,
        'LANDING_PAGE_URL': settings.LANDING_PAGE_URL,
    }
