# Generated by Django 4.1.7 on 2023-05-13 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("administration", "0015_userprofile"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="image",
            field=models.ImageField(default="default.jpg", upload_to="profile_pics/"),
        ),
    ]