from abc import ABC, abstractmethod


class AbstractEventReceiver(ABC):
    """Abstract EventReceiver class."""

    @abstractmethod
    def save(self, decoded_event):
        pass
