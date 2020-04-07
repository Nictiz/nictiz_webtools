# Generated by Django 2.2.11 on 2020-03-24 09:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0090_auto_20200324_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mappingreleasecandidaterules',
            name='export_rule',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mapping.MappingRule'),
        ),
        migrations.AlterField(
            model_name='mappingreleasecandidaterules',
            name='export_task',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mapping.MappingTask'),
        ),
    ]