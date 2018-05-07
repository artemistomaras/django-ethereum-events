from django.contrib import admin
from solo.admin import SingletonModelAdmin

from django_ethereum_events.models import Daemon

admin.site.register(Daemon, SingletonModelAdmin)
