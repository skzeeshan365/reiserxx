from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Logs(models.Model):
    name = models.CharField(max_length=100)
    short_desc = models.CharField(max_length=200, default='not provided')
    desc = models.TextField()
    timestamp = models.DateTimeField(max_length=50, auto_now=True)


class Images(models.Model):
    log = models.ForeignKey(Logs, related_name='images', on_delete=models.CASCADE)
    img = models.ImageField(upload_to='pics', default='None')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=1000, blank=True)

    # Create a user profile for each user
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    # Connect the user profile creation to the User model's post_save signal
    from django.db.models.signals import post_save
    post_save.connect(create_user_profile, sender=User)
