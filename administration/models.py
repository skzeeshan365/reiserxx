from django.db import models
from time import gmtime, strftime
from datetime import datetime


# Create your models here.


class Logs(models.Model):
    name = models.CharField(max_length=100)
    short_desc = models.CharField(max_length=200, default='not provided')
    desc = models.TextField()
    img = models.ImageField(upload_to='pics', default='None')
    timestamp = models.DateTimeField(max_length=50, auto_now=True)