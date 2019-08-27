######################
django-ethereum-events
######################

Ethereum Contract Event Log monitoring in Django

.. image:: https://travis-ci.org/artemistomaras/django-ethereum-events.svg?branch=master
    :target: https://travis-ci.org/artemistomaras/django-ethereum-events
    
.. image:: https://img.shields.io/pypi/v/django-ethereum-events.svg   
    :target: https://pypi.python.org/pypi/django-ethereum-events
    
    
********
Overview
********

This package provides an easy way to monitor an ethereum blockchain for transactions that invoke `Contract Events`_ that are of particular interest.

The main concept was inspired by the following project:

- https://github.com/gnosis/django-eth-events

Package versions **0.2.x+** support **web3 v4**.

If you want python 2.7 compatibility and/or **web3 v3** support, use version **0.1.x** of this package.


.. _`Contract Events`: http://solidity.readthedocs.io/en/develop/contracts.html#events 

************
Installation
************

1.  Install using pip:

    ::

        pip install django-ethereum-events


2.  Make sure to include ``'django_ethereum_events'`` in your ``INSTALLED_APPS``

    .. code-block:: python

        INSTALLED_APPS += ('django_ethereum_events')
    
    if you are using the **admin backend**, also include ``solo`` in your ``INSTALLED_APPS``.
   
3.  Make necessary migrations

    .. code-block:: python

        python manage.py migrate django_ethereum_events


*****
Usage
*****

1.  In your ``settings`` file, specify the following settings

    .. code-block:: python

        ETHEREUM_NODE_URI = 'http://localhost:8545'
         
         
2.  Create a new MonitoredEvent
    
    .. code-block:: python
    
        contract_abi = """
        The whole contract abi goes here
        """
        
        event = "MyEvent"  # the emitted event name
        event_receiver = "myapp.event_receivers.CustomEventReceiver"
        contract_address = "0x10f683d9acc908cA6b7A34726271229B846b0292"  # the address of the contract emitting the event
        
        MonitoredEvent.object.register_event(
            event_name=event,
            contract_address=contract_address,
            contract_abi=contract_abi,
            event_receiver=event_receiver
        )
        
3.  Create an appropriate event receiver

    .. code-block:: python

        from django_ethereum_events.chainevents import AbstractEventReceiver

        class CustomEventReceiver(AbsractEventReceiver):
            def save(self, decoded_event):
                # custom logic goes here

    The ``decoded_event`` parameter is the decoded log as provided from `web3.utils.events.get_event_data`_ method.
    
    .. _`web3.utils.events.get_event_data`: https://github.com/ethereum/web3.py/blob/v4.9.2/web3/utils/events.py#L148

4.  To start monitoring the blockchain, either run the celery task ``django_ethereum_events.tasks.event_listener`` or better, use ``celerybeat`` to run it as a periodical task

    .. code-block:: python

        from celery.beat import crontab

        CELERYBEAT_SCHEDULE = {
        'ethereum_events': {
            'task': 'django_ethereum_events.tasks.event_listener',
            'schedule': crontab(minute='*/1')  # run every minute
            }
        }

    You can also set the optional ``ETHEREUM_LOGS_BATCH_SIZE`` setting which limits the maximum amount of the blocks that can be read at a time from the celery task.


******************************
More about the event receivers
******************************

It is advisable that the code inside the custom event receiver to be simple since it is run synchronously while the ``event_listener`` task is running. If that is not the case, pass the argument ``decoded_event`` to a celery task of your own

.. code-block:: python

    # inside the CustomEventReceiver.save method
    from django_ethereum_events.utils import HexJsonEncoder
    decoded_event_data = json.dumps(decoded_event, cls=HexJsonEncoder)
    my_custom_task.delay(decoded_event_data)
        
   
If an unhandled exception is raised inside the event receiver, the ``event_listener`` task logs the error and creates
a new instance of the ``django_ethereum_events.models.FailedEventLog`` containing all the relevant event information.

The event listener does **not** attempt to rerun ``FailedEventLogs``. That is up to the client implementation.


****************************
Resetting the internal state
****************************
Blocks are processed only once. The last block processed is stored in the ``.models.Daemon`` entry.

To reset the number of blocks processed, run the ``reset_block_daemon`` command optionally specifying the block number (-b, --block) to reset to (defaults to zero). If you reset it to zero, the next time the ``event_listener`` is fired, it will start processing blocks from the genesis block.

The ``Daemon`` entry can also be changed from the django admin backend.

***************************
Proof-of-Authority Networks
***************************
To use this package on **Rinkeby** or any other private network that uses the Proof-of-Authority consensus engine (also named clique), set the optional ``ETHEREUM_GETH_POA`` setting to ``True``.
