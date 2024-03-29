# Generated by Django 4.2.1 on 2023-05-16 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0018_alter_post_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contact",
            name="email",
            field=models.EmailField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="tag",
            name="tag",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
