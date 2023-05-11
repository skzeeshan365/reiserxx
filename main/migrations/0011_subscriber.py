# Generated by Django 4.1.7 on 2023-05-10 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0010_contact"),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscriber",
            fields=[
                (
                    "id",
                    models.CharField(
                        default="vJ1oKUtcEhEsrPFq",
                        editable=False,
                        max_length=16,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("verified", models.BooleanField(default=False)),
            ],
        ),
    ]
