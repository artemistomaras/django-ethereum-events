import inspect
import json

from django import forms
from django.forms import widgets
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _
from eth_utils import is_hex_address, event_abi_to_log_topic, add_0x_prefix
from web3 import Web3

from .models import MonitoredEvent
from .chainevents import AbstractEventReceiver
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

        if isinstance(contract_abi, str):
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
            get_event_abi(abi, name)
        except ValueError:
            raise forms.ValidationError(_('Event %(name)s cannot be found in the given contract ABI') % {'name': name})

    def save(self, commit=True):
        cd = self.cleaned_data
        contract_abi = cd['contract_abi']

        event = super(MonitoredEventForm, self).save(commit=False)  # event is not ready to be saved

        event_abi = get_event_abi(contract_abi, event.name)
        topic = event_abi_to_log_topic(event_abi)
        event.topic = add_0x_prefix(topic.hex())
        event.event_abi = json.dumps(event_abi)
        event.save()

        return event
