import logging
from contextlib import contextmanager

from celery import shared_task

from django.core.cache import cache

from .event_listener import EventListener


LOCK_KEY = '_django_ethereum_events_cache_lock'
LOCK_VALUE = 'LOCK'
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
        if status:
            cache.delete(lock_id)


@shared_task
def event_listener():
    """
    Celery task that transverses the blockchain looking for event logs.

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
    with cache_lock(LOCK_KEY, LOCK_VALUE) as acquired:
        if acquired:
            listener = EventListener()
            try:
                listener.execute()
            except Exception:
                logger.exception('Exception while running event listener task', exc_info=True)
                daemon = listener.daemon
                last_processed_block = daemon.block_number
                daemon.last_error_block_number = last_processed_block + 1
                daemon.save()
        else:
            logger.info('Event listener is already running. Skipping execution.')
