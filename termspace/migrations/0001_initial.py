# Generated by Django 2.2.9 on 2020-01-20 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TermspaceComments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(max_length=300)),
                ('assignee', models.CharField(max_length=300)),
                ('status', models.CharField(max_length=300)),
                ('folder', models.CharField(max_length=300)),
                ('time', models.CharField(max_length=300)),
                ('comment', models.TextField()),
            ],
        ),
    ]