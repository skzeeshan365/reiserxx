# Generated by Django 4.1.7 on 2023-05-11 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0011_subscriber"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscriber",
            name="id",
            field=models.CharField(
                editable=False,
                max_length=32,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
