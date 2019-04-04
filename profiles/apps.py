from django.apps import AppConfig

class ProfilesConfig(AppConfig):
    name = 'profiles'
    verbose_name = 'User Profiles'

    def ready(self):
        "Signal receivers with the @receiver decorator will be connected"
        import profiles.signals
