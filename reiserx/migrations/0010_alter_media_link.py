# Generated by Django 4.0.6 on 2022-08-07 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reiserx', '0009_remove_message_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='link',
            field=models.URLField(),
        ),
    ]
