from django.apps import AppConfig

class LiteracyEventsConfig(AppConfig):
    name = 'literacy_events'
    verbose_name = 'Literacy events'

    def ready(self):
        "Signal receivers with the @receiver decorator will be connected"
        import literacy_events.signals
