# Generated by Django 4.0.6 on 2022-08-07 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0003_alter_logs_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logs',
            name='timestamp',
            field=models.DateTimeField(verbose_name='2022-08-07 23:58:46'),
        ),
    ]
