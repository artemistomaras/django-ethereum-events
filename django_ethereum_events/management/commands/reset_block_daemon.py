from django.core.management import BaseCommand

from django_ethereum_events.models import Daemon


class Command(BaseCommand):
    help = 'Resets the internal ethereum block number counter.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-b',
            '--block',
            nargs='?',
            type=int,
            action='store',
            dest='block',
            default=0,
            help='Block number to reset the counter to'
        )

    def handle(self, *args, **options):
        block_number = options['block']
        d = Daemon.get_solo()
        d.block_number = block_number
        d.last_error_block_number = 0
        d.save()

        self.stdout.write(self.style.SUCCESS(
            'Internal block number counter reset to {0}.'.format(block_number)
        ))
