import json

from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel

CACHE_UPDATE_KEY = '_django_ethereum_events_update_required'


class Daemon(SingletonModel):
    """Model responsible for storing blockchain related information."""
    block_number = models.IntegerField(default=0)
    last_error_block_number = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class EventManager(models.Manager):
    @staticmethod
    def register_event(event_name, contract_address, contract_abi, event_receiver):
        from .forms import MonitoredEventForm
        form = MonitoredEventForm({
            'name': event_name,
            'contract_address': contract_address,
            'event_receiver': event_receiver,
            'contract_abi': contract_abi
        })

        if form.is_valid():
            event = form.save()
            return event

        raise ValueError('The following arguments are invalid \n{}'.format(form.errors.as_text()))


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


class FailedEventLog(models.Model):
    """This model holds the event logs that raised an Exception inside the client's
    event_receiver method and was left unhandled.

    When a decode log that is passed inside the client's implementation of the `AbstractEventReceiver`
    raises an exception, the `EventListener` is not halted. Instead, the event log that caused
    the unhandled expeption is stored in this model, along with all the information for the user to
    `reply` the invocation of the custom `event_receiver` implementation.
    """
    event = models.CharField(max_length=256)
    transaction_hash = models.CharField(max_length=66, validators=[MinLengthValidator(66)])
    transaction_index = models.IntegerField()
    block_hash = models.CharField(max_length=66, validators=[MinLengthValidator(66)])
    block_number = models.IntegerField()
    log_index = models.IntegerField()
    address = models.CharField(max_length=42, validators=[MinLengthValidator(42)])
    args = models.TextField(default="{}")
    monitored_event = models.ForeignKey(MonitoredEvent, related_name='failed_events', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Failed to process Event')
        verbose_name_plural = _('Failed to process Events')

    def __str__(self):
        return self.event

