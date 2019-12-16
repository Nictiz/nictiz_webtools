# Generated by Django 2.2.7 on 2019-11-14 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snomed_list_generator', '0002_auto_20191114_1359'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='snomedlistgeneratorlog',
            name='query',
        ),
        migrations.AddField(
            model_name='snomedlistgeneratorlog',
            name='conceptFSN',
            field=models.CharField(default='onbekend', max_length=500),
        ),
        migrations.AddField(
            model_name='snomedlistgeneratorlog',
            name='searchterm',
            field=models.CharField(default='onbekend', max_length=30),
        ),
    ]
