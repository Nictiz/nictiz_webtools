# Generated by Django 3.1.7 on 2021-04-22 07:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mapping", "0120_mappingreleasecandidate_import_all"),
    ]

    operations = [
        migrations.AddField(
            model_name="mappingproject",
            name="automap_valueset",
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
    ]
