# Generated by Django 4.1.7 on 2023-05-11 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0014_alter_subscriber_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscriber",
            name="id",
            field=models.CharField(
                editable=False,
                max_length=36,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
