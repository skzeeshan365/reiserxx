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


class ChangeLog(models.Model):
    version = models.FloatField()


class ChangeLogData(models.Model):
    changelog = models.ForeignKey(ChangeLog, related_name='logdata', on_delete=models.CASCADE)
    logs = models.CharField(max_length=200)


class Contact(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=70,blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(max_length=50, auto_now=True)