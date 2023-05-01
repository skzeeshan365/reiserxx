from django.db import models


# Create your models here.


class Logs(models.Model):
    name = models.CharField(max_length=100)
    short_desc = models.CharField(max_length=200, default='not provided')
    desc = models.TextField()
    timestamp = models.DateTimeField(max_length=50, auto_now=True)


class Images(models.Model):
    log = models.ForeignKey(Logs, related_name='images', on_delete=models.CASCADE)
    img = models.ImageField(upload_to='pics', default='None')