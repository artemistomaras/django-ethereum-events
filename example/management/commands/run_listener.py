from django.core.management import BaseCommand

from django_ethereum_events.tasks import event_listener


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Running listener...')
        event_listener()
        print('Listener terminated...')
