# Generated by Django 2.2.6 on 2019-10-17 12:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mapping", "0008_auto_20191017_1224"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mappingrule",
            name="source_component",
            field=models.CharField(default=2, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="mappingrule",
            name="target_component",
            field=models.CharField(default=6, max_length=50),
            preserve_default=False,
        ),
    ]
