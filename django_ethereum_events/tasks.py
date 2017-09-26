import logging
from contextlib import contextmanager
from .event_listener import EventListener
from django.core.cache import cache
from celery import shared_task
from .models import Daemon

lock_value = 'LOCK'
logger = logging.getLogger(__name__)


@contextmanager
def cache_lock(lock_id, lock_value):
    # cache.add fails if the key already exists
    status = cache.add(lock_id, lock_value)
    try:
        yield status
    finally:
        cache.delete(lock_id)


@shared_task
def event_listener():
    with cache_lock('DJANGO_ETHEREUM_EVENTS', lock_value) as acquired:
        if acquired:
            listener = EventListener()
            try:
                listener.execute()
            except Exception as e:
                logger.error(str(e))
                daemon = Daemon.get_solo()
                last_error_block_number = daemon.last_error_block_number
                current_block_number = daemon.block_number
                if last_error_block_number < current_block_number:
                    daemon.last_error_block_number = current_block_number
                    daemon.save()
