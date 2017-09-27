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
    """Cache based locking mechanism.

    Cache backends `memcached` and `redis` are recommended.
    """
    # cache.add fails if the key already exists
    status = cache.add(lock_id, lock_value)
    try:
        yield status
    finally:
        cache.delete(lock_id)


@shared_task
def event_listener():
    """Celery task that transverses the blockchain looking for event logs.

    This task should be run periodically via celerybeat to monitor for
    new blocks in the blockchain.

    Examples:
        CELERYBEAT_SCHEDULE = {
            'ethereum_events': {
                'task': 'django_ethereum_events.tasks.event_listener',
                'schedule': crontab(minute='*/2')  # run every 2 minutes
            }
        }
    """
    with cache_lock('DJANGO_ETHEREUM_EVENTS', lock_value) as acquired:
        if acquired:
            listener = EventListener()
            try:
                listener.execute()
            except Exception as e:
                logger.error(str(e))
                # Save error state
                daemon = Daemon.get_solo()
                last_error_block_number = daemon.last_error_block_number
                current_block_number = daemon.block_number
                if last_error_block_number < current_block_number:
                    daemon.last_error_block_number = current_block_number
                    daemon.save()
