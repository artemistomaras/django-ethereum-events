import inspect
import json

from django import forms
from django.forms import widgets
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from eth_utils import add_0x_prefix, event_abi_to_log_topic, is_hex_address

from web3 import Web3

from .chainevents import AbstractEventReceiver
from .models import MonitoredEvent
from .utils import get_event_abi


class MonitoredEventForm(forms.ModelForm):
    name = forms.CharField(max_length=256)
    contract_address = forms.CharField(max_length=42, min_length=42)
    contract_abi = forms.Field(widget=widgets.Textarea)
    event_receiver = forms.CharField(max_length=256)

    class Meta:
        model = MonitoredEvent
        fields = ('name', 'contract_address', 'event_receiver')

    def clean_contract_address(self):
        contract_address = self.cleaned_data['contract_address']

        if not is_hex_address(contract_address):
            raise forms.ValidationError(
                _('Contract address %(address)s is not a valid hex address') % {'address': contract_address})
        return Web3.toChecksumAddress(contract_address)

    def clean_contract_abi(self):
        contract_abi = self.cleaned_data['contract_abi']
        is_str = isinstance(contract_abi, str)
        is_list = isinstance(contract_abi, list)

        if not (is_str or is_list):
            raise forms.ValidationError(_('Contract abi must be either `str` or `list`'))

        if is_str:
            try:
                contract_abi = json.loads(contract_abi)
            except Exception:
                raise forms.ValidationError(_('Invalid contract abi'))

        return contract_abi

    def clean_event_receiver(self):
        event_receiver = self.cleaned_data['event_receiver']

        try:
            event_handler_cls = import_string(event_receiver)
            if not inspect.isclass(event_handler_cls) or not issubclass(event_handler_cls, AbstractEventReceiver):
                raise forms.ValidationError(
                    _('%(receiver)s is not a valid subclass of AbstractEventReceiver') % {'receiver': event_receiver})
        except ImportError:
            raise forms.ValidationError(_('Cannot import module %(module)s') % {'module': event_receiver})

        return event_receiver

    def clean(self):
        cleaned_data = super().clean()

        name = cleaned_data.get('name')
        abi = cleaned_data.get('contract_abi')

        try:
            self._event_abi = get_event_abi(abi, name)
        except ValueError:
            raise forms.ValidationError(_('Event %(name)s cannot be found in the given contract ABI') % {'name': name})

    def save(self, commit=True):
        event = super(MonitoredEventForm, self).save(commit=False)  # event is not ready to be saved

        topic = event_abi_to_log_topic(self._event_abi)
        event.topic = add_0x_prefix(topic.hex())
        event.event_abi = json.dumps(self._event_abi)
        event.save()

        return event
