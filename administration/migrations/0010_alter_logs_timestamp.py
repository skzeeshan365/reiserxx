# Generated by Django 4.0.6 on 2022-08-08 00:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0009_alter_logs_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logs',
            name='timestamp',
            field=models.CharField(default=datetime.datetime.now, max_length=50),
        ),
    ]
