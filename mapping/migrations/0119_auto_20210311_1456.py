# Generated by Django 3.1.7 on 2021-03-11 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0118_auto_20210302_1154'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='mappingcodesystemcomponent',
            index=models.Index(fields=['component_id'], name='mapping_map_compone_ecd574_idx'),
        ),
    ]
