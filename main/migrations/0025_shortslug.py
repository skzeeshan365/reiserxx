# Generated by Django 4.2.2 on 2023-10-08 15:30

from django.db import migrations, models
import django.db.models.deletion
import shortuuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0024_remove_post_timestamp_post_timestamp_created_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShortSlug",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "short_slug",
                    shortuuidfield.fields.ShortUUIDField(
                        blank=True, editable=False, max_length=22, unique=True
                    ),
                ),
                (
                    "post",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="main.post"
                    ),
                ),
            ],
        ),
    ]