from django.core.management import BaseCommand
from django_ethereum_events.models import Daemon, MonitoredEvent, FailedEventLog



class Command(BaseCommand):
    """Use only for development!
    """
    help = 'Cleans the app state (only for dev!)'

    def handle(self, *args, **options):
        Daemon.get_solo().delete()
        self.stdout.write(self.style.SUCCESS('Reset block monitoring to 0...'))

        MonitoredEvent.objects.all().update(monitored_from=None)
        FailedEventLog.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted failed event logs...'))