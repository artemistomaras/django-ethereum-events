from django.contrib import admin

from solo.admin import SingletonModelAdmin

from .models import Daemon

admin.site.register(Daemon, SingletonModelAdmin)
