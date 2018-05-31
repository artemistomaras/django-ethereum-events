import inspect
import json

from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _
from eth_utils import is_hex_address, event_abi_to_log_topic, add_0x_prefix
from solo.models import SingletonModel
from web3 import Web3

from django_ethereum_events.chainevents import AbstractEventReceiver
from django_ethereum_events.utils import get_event_abi


class Daemon(SingletonModel):
    """Model responsible for storing blockchain related information."""
    block_number = models.IntegerField(default=0)
    last_error_block_number = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class EventManager(models.Manager):
    def register_event(self, event_name, contract_address, contract_abi, event_receiver):
        if not is_hex_address(contract_address):
            raise ValueError('Contract address is not a valid hex address')

        event_handler_cls = import_string(event_receiver)
        if not inspect.isclass(event_handler_cls) or not issubclass(event_handler_cls, AbstractEventReceiver):
            raise TypeError('{} is not a valid subclass of AbstractEventReceiver class')

        if isinstance(contract_abi, str):
            contract_abi = json.loads(contract_abi)

        event_abi = get_event_abi(contract_abi, event_name)
        topic = event_abi_to_log_topic(event_abi)

        monitored_event = self.model(
            name=event_name,
            contract_address=Web3.toChecksumAddress(contract_address),
            topic=add_0x_prefix(topic.hex()),
            event_abi=json.dumps(event_abi),
            event_receiver=event_receiver
        )

        monitored_event.save()
        return monitored_event


class MonitoredEvent(models.Model):
    name = models.CharField(max_length=256)
    contract_address = models.CharField(max_length=42, validators=[MinLengthValidator(42)])
    event_abi = models.TextField()
    topic = models.CharField(max_length=66, validators=[MinLengthValidator(66)])
    event_receiver = models.CharField(max_length=256)
    monitored_from = models.IntegerField(blank=True, null=True,
                                         help_text=_('Block number in which monitoring for this event started'))

    objects = EventManager()

    class Meta:
        verbose_name = _('Monitored Event')
        verbose_name_plural = _('Monitored Events')
        unique_together = ('topic', 'contract_address')

    def __str__(self):
        return '{} at {}'.format(self.name, self.contract_address)

    @property
    def event_abi_parsed(self):
        if hasattr(self, '_event_abi_parsed'):
            return self._event_abi_parsed

        self._event_abi_parsed = json.loads(self.event_abi)
        return self._event_abi_parsed
