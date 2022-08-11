from django.contrib import admin
from .models import Media
from .models import Message
from .models import ChangeLog
from .models import ChangeLogData
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
