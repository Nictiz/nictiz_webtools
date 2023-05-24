# Generated by Django 4.0 on 2023-05-07 08:56

import app.model_fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0127_auto_20230406_0933'),
    ]

    operations = [
        migrations.AddField(
            model_name='mappingeclconcept',
            name='is_deleted',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='mappingeclconcept',
            name='is_new',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='mappingreleasecandidate',
            name='export_project',
            field=models.ManyToManyField(blank=True, related_name='project', to='mapping.MappingProject'),
        ),
        migrations.AlterField(
            model_name='mappingreleasecandidaterules',
            name='accepted',
            field=app.model_fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='mappingreleasecandidaterules',
            name='rejected',
            field=app.model_fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='mappingtask',
            name='exclusions',
            field=app.model_fields.ArrayField(base_field=models.CharField(max_length=20), blank=True, null=True, size=None),
        ),
    ]