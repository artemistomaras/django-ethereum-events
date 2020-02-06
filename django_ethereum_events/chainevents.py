from abc import ABCMeta, abstractmethod

try:
    # Django 1.11.x - 2.x
    from django.utils.six import with_metaclass
except ImportError:
    # Django 3.x
    from six import with_metaclass


class AbstractEventReceiver(with_metaclass(ABCMeta)):
    """Abstract EventReceiver class.

    For every Event that is monitored, an Event handler that inherits
    this class must be created and the `save` method must be implemented.
    """

    @abstractmethod
    def save(self, decoded_event):
        pass
