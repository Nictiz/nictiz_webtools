# Generated by Django 3.1.7 on 2021-03-15 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0119_auto_20210311_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='mappingreleasecandidate',
            name='import_all',
            field=models.BooleanField(default=False),
        ),
    ]
