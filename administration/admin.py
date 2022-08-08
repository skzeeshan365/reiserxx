from django.contrib import admin
from .models import Logs
from .models import Images


# Register your models here.

class ImagesInline(admin.StackedInline):
    model = Images


class LogsAdmin(admin.ModelAdmin):
    inlines = [
        ImagesInline
    ]


admin.site.register(Logs, LogsAdmin)
admin.site.register(Images)

