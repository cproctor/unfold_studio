from django.conf import settings # import the settings file

def documentation_urls(request):
    return {
        'DOCUMENTATION_URL': settings.DOCUMENTATION_URL,
        'HELP_URL': settings.HELP_URL,
        'TEACHING_URL': settings.TEACHING_URL,
        'DEBUG': settings.DEBUG
    }
