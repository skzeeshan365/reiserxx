from django.db import models
from pytz import timezone
from datetime import datetime


# Create your models here.
class Logs(models.Model):
    name = models.CharField(max_length=100)
    short_desc = models.CharField(max_length=200, default='not provided')
    desc = models.TextField()
    img = models.ImageField(upload_to='pics', default='None')
    ind_time = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S.%f')
    timestamp = models.CharField(max_length=50, default=ind_time)
