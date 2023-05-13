from io import BytesIO

from PIL import Image
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import Images
from .models import Logs, UserProfile


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

    def save_model(self, request, obj, form, change):
        if obj.image:
            # Open the image from the file
            img = Image.open(obj.image.file)

            # Resize the image if necessary
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)

                # Save the resized image to a buffer
                buffer = BytesIO()
                img.save(buffer, format='JPEG')

                # Create a new InMemoryUploadedFile object from the buffer
                file = InMemoryUploadedFile(buffer, 'ImageField', obj.image.name, 'image/jpeg', buffer.getbuffer().nbytes, None)

                # Replace the original image file with the resized image file
                obj.image = file

        super().save_model(request, obj, form, change)