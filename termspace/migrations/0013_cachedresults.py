# Generated by Django 2.2.16 on 2020-09-25 13:03

import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('termspace', '0012_snomedtree'),
    ]

    operations = [
        migrations.CreateModel(
            name='cachedResults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('title', models.CharField(max_length=500)),
                ('finished', models.BooleanField(default=False)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=None, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True)),
            ],
        ),
    ]
