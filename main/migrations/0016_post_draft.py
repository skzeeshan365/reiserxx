# Generated by Django 4.1.7 on 2023-05-12 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0015_alter_subscriber_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="draft",
            field=models.BooleanField(default=False),
        ),
    ]