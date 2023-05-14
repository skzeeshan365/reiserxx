from django.contrib import admin

from .models import ChangeLog
from .models import ChangeLogData
from .models import Contact
from .models import DriverDownloadUrl
from .models import Media
from .models import Message


# Register your models here.


class ChangeLogDataInline(admin.StackedInline):
    model = ChangeLogData


class ChangeLogAdmin(admin.ModelAdmin):
    inlines = [
        ChangeLogDataInline
    ]


admin.site.register(ChangeLog, ChangeLogAdmin)
admin.site.register(ChangeLogData)
admin.site.register(Media)
admin.site.register(Message)
admin.site.register(DriverDownloadUrl)
admin.site.register(Contact)
