from django.apps import AppConfig
from django.conf import settings


class EthereumEventsConfig(AppConfig):
    name = 'django_ethereum_events'

    def ready(self):
        super(EthereumEventsConfig, self).ready()
        app.config_from_object('django.conf:settings')
        app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, force=True)
