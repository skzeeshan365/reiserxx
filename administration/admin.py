from io import BytesIO

from PIL import Image
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

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


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, UserProfile) and instance.image:
                # Open the image from the file
                img = Image.open(instance.image)

                # Resize the image if necessary
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)

                    # Create a new temporary in-memory file
                    tmp_buffer = BytesIO()
                    img.save(tmp_buffer, format='WEBP', quality=70)

                    # Create a new SimpleUploadedFile from the buffer
                    tmp_file = SimpleUploadedFile('resized_image.jpg', tmp_buffer.getvalue())

                    # Assign the resized image file to the instance

                    instance.image = tmp_file

        formset.save()



# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)