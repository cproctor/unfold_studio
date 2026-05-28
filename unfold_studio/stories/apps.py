from django.apps import AppConfig


class StoriesConfig(AppConfig):
    name = "stories"
    verbose_name = "Stories"

    def ready(self):
        import stories.signals  # noqa: F401
