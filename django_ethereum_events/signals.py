from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .utils import refresh_cache_update_value
from .models import MonitoredEvent


@receiver(post_save, sender=MonitoredEvent)
def monitored_event_created_or_updated(**kwargs):
    refresh_cache_update_value(update_required=True)


@receiver(post_delete, sender=MonitoredEvent)
def monitored_event_deleted(**kwargs):
    refresh_cache_update_value(update_required=True)