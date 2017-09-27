######################
django-ethereum-events
######################

Ethereum Event Log monitoring in Django

.. image:: https://travis-ci.org/artemistomaras/django-ethereum-events.svg?branch=master
    :target: https://travis-ci.org/artemistomaras/django-ethereum-events

********
Overview
********

This package provides an easy way to monitor an ethereum blockchain for transactions that invoke `Contract Events`_ that are of particular interest.

The main concept was inspired by the following project:

- https://github.com/gnosis/django-eth-events

.. _`Contract Events`: http://solidity.readthedocs.io/en/develop/contracts.html#events 

************
Installation
************

1.  Either checkout ``django-ethereum-events`` from GitHub, or install using pip:

::

    pip install django-ethereum-events


2.  Make sure to include ``'django_ethereum_events'`` in your ``INSTALLED_APPS``

::

    INSTALLED_APPS += ('django_ethereum_events')
   
   
3.  Make necassery migrations

::

    python manage.py makemigrations django-ethereum_events


*****
Usage
*****

1.  In your ``settings`` file, specify the following settings

::

    ETHEREUM_NODE_HOST = 'localhost'
    ETHEREUM_NODE_PORT = 8545
    ETHEREUM_NODE_SSL = False
    ETHEREUM_EVENTS = []
 
 
2.  ``ETHEREUM_EVENTS`` parameter is a list of that holds information about the specific events to monitor for.
Its syntax is the following

::

    ETHEREUM_EVENTS = [
        {
            'CONTRACT_ADDRESS': 'contract address',
            'EVENT_ABI': 'abi of the event(not the whole contract abi)',
            'EVENT_RECEIVER': 'custom event handler'
        }    
    ]


3.  Create an appropriate ``EVENT_RECEIVER``

::

    from django_ethereum_events.chainevents import AbstractEventReceiver
    
    class CustomEventReceiver(AbsractEventReceiver):
        def save(self, decoded_event):
            # custom logic goes here
            
The ``decoded_event`` parameter is the decoded log as provided from `web3.utils.events.get_event_data`_ method.
    
.. _`web3.utils.events.get_event_data`: https://github.com/pipermerriam/web3.py/blob/master/web3/utils/events.py#L140


4.  To start monitoring the blockchain, either run the celery task ``django_ethereum_events.tasks.event_listener`` or better, use ``celerybeat`` to run it as a periodical task

::

    from celery.beat import crontab
    
    CELERYBEAT_SCHEDULE = {
    'ethereum_events': {
        'task': 'django_ethereum_events.tasks.event_listener',
        'schedule': crontab(minute='*/5')  # run every 5 minutes
        }
    }
