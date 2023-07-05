# Generated by Django 2.2.16 on 2020-10-29 11:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mapping", "0109_auto_20200929_1019"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mappingreleasecandidate",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("0", "draft"),
                    ("1", "active"),
                    ("2", "retired"),
                    ("3", "unknown"),
                ],
                default=None,
                max_length=50,
                null=True,
            ),
        ),
    ]
