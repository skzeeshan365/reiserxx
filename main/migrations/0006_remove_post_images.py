# Generated by Django 4.1.7 on 2023-04-30 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_post_images_alter_post_content"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="images",
        ),
    ]
