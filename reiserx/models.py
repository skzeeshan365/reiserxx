from django.db import models


# Create your models here.

class Media(models.Model):
    name = models.CharField(max_length=100)
    desc = models.TextField()
    img = models.ImageField(upload_to='pics')
    link = models.URLField()
    isInternal = models.BooleanField(default=False)
    timestamp = models.DateField(default='2022-07-22')


class Message(models.Model):
    message = models.TextField()

