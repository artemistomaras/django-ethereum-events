import json

from django.core.management import BaseCommand

from django_ethereum_events.chainevents import AbstractEventReceiver
from django_ethereum_events.models import MonitoredEvent

echo_address = "0xCfEB869F69431e42cdB54A4F4f105C19C080A601"
echo_abi = json.loads("""
[
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "name": "message",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "sender",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "LogEcho",
      "type": "event"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "message",
          "type": "string"
        }
      ],
      "name": "echo",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]
""")


class TestReceiver(AbstractEventReceiver):

    def save(self, decoded_event):
        print('Received event: {}'.format(decoded_event))


receiver = 'example.management.commands.register_events.TestReceiver'

# List of ethereum events to monitor the blockchain for
DEFAULT_EVENTS = [
    ('LogEcho', echo_address, echo_abi, receiver),
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        monitored_events = MonitoredEvent.objects.all()
        for event in DEFAULT_EVENTS:

            if not monitored_events.filter(name=event[0], contract_address__iexact=event[1]).exists():
                self.stdout.write('Creating monitor for event {} at {}'.format(event[0], event[1]))

                MonitoredEvent.objects.register_event(*event)

        self.stdout.write(self.style.SUCCESS('Events are up to date'))
