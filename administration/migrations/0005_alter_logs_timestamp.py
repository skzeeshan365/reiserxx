# Generated by Django 4.0.6 on 2022-08-08 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0004_alter_logs_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logs',
            name='timestamp',
            field=models.DateTimeField(default='2022-08-08 00:00:58'),
        ),
    ]
