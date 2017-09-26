from ..chainevents import AbstractEventReceiver

data = []


class DepositEventReceiver(AbstractEventReceiver):
    def save(self, decoded_event):
        data.append(decoded_event)
