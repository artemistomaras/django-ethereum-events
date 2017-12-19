from django.db import models

from solo.models import SingletonModel


class Daemon(SingletonModel):
    """Model responsible for storing blockchain related information."""

    block_number = models.IntegerField(default=0)
    last_error_block_number = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
