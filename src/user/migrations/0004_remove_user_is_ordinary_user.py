# Generated by Django 4.2 on 2025-04-04 17:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_user_is_ordinary_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="is_ordinary_user",
        ),
    ]
