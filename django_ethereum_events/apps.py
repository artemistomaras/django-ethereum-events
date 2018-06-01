from django.apps import AppConfig


class EthereumEventsConfig(AppConfig):
    name = 'django_ethereum_events'

    def ready(self):
        super().ready()

        import django_ethereum_events.signals  # noqa