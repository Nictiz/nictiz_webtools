# Generated by Django 3.1.7 on 2021-03-02 10:33

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('termspace', '0013_cachedresults'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cachedresults',
            name='data',
            field=models.JSONField(blank=True, default=None, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True),
        ),
        migrations.AlterField(
            model_name='snomedtree',
            name='data',
            field=models.JSONField(blank=True, default=None, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True),
        ),
        migrations.AlterField(
            model_name='termspacetask',
            name='data',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]
