from django.db import models


# Create your models here.

class Media(models.Model):
    name = models.CharField(max_length=100)
    desc = models.TextField()
    img = models.ImageField(upload_to='pics')
    link = models.TextField()
