# Generated by Django 2.2.6 on 2019-10-16 13:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("mapping", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="MappingCodesystems",
            new_name="MappingCodesystem",
        ),
        migrations.RenameModel(
            old_name="MappingProjects",
            new_name="MappingProject",
        ),
        migrations.RenameModel(
            old_name="MappingRules",
            new_name="MappingRule",
        ),
        migrations.RenameModel(
            old_name="MappingTasks",
            new_name="MappingTask",
        ),
    ]
