# Generated by Django 4.1.7 on 2023-04-29 16:10

import cloudinary.models
from django.db import migrations
import froala_editor.fields


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_alter_post_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="images",
            field=cloudinary.models.CloudinaryField(
                blank=True, max_length=255, null=True, verbose_name="images"
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="content",
            field=froala_editor.fields.FroalaField(),
        ),
    ]
