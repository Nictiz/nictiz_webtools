# Generated by Django 2.2.13 on 2020-06-24 07:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mapping", "0101_auto_20200622_1702"),
    ]

    operations = [
        migrations.AddField(
            model_name="mappingtaskaudit",
            name="sticky",
            field=models.BooleanField(default=False),
        ),
    ]
