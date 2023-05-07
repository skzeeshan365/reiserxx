from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Logs, UserProfile
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


# Define an inline admin for UserProfile that will be shown on the User admin page
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

# Define a new User admin that includes the UserProfile inline
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register UserProfile with the admin site
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')