# Generated by Django 4.0.6 on 2022-08-11 16:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reiserx', '0011_changelog_changelogdata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changelogdata',
            name='parentKey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logdata', to='reiserx.changelog'),
        ),
    ]
