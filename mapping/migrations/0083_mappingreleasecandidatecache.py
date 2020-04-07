# Generated by Django 2.2.9 on 2020-03-16 06:53

import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0082_auto_20200307_0131'),
    ]

    operations = [
        migrations.CreateModel(
            name='MappingReleaseCandidateCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True, default=None, null=True)),
                ('release_notes', models.TextField(blank=True, default=None, null=True)),
                ('finished', models.BooleanField(default=False)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('codesystem', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='source_codesystem_for_rc', to='mapping.MappingCodesystem')),
            ],
        ),
    ]