from django.contrib import admin

from solo.admin import SingletonModelAdmin

from .forms import MonitoredEventForm
from .models import Daemon, FailedEventLog, MonitoredEvent

admin.site.register(Daemon, SingletonModelAdmin)


class MonitoredEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'contract_address', 'topic', 'event_receiver', 'monitored_from']
    list_filter = ['contract_address']
    search_fields = ['name', 'contract_address']

    add_form = MonitoredEventForm

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super(MonitoredEventAdmin, self).get_form(request, obj, **defaults)


admin.site.register(MonitoredEvent, MonitoredEventAdmin)


class FailedEventLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'block_number', 'log_index', 'address', 'transaction_hash', 'created']
    list_filter = ['address']
    search_fields = ['event']


admin.site.register(FailedEventLog, FailedEventLogAdmin)
