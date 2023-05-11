# Generated by Django 4.1.7 on 2023-05-11 02:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0013_alter_subscriber_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscriber",
            name="email",
            field=models.EmailField(
                error_messages={
                    "unique": "Looks like you're already on our VIP list! Time to sit back, relax and enjoy the exclusive perks of being one of our favorites"
                },
                max_length=254,
                unique=True,
            ),
        ),
    ]
