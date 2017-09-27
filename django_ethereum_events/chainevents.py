from abc import ABC, abstractmethod


class AbstractEventReceiver(ABC):
    """Abstract EventReceiver class.

    For every Event that is monitored, an Event handler that inherits
    this class must be created and the `save` method must be implemented.
    """

    @abstractmethod
    def save(self, decoded_event):
        pass
