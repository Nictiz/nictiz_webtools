# Generated by Django 2.2.6 on 2019-10-30 15:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("mapping", "0043_mappingeventlog_action_user"),
    ]

    operations = [
        migrations.CreateModel(
            name="MappingCorrelation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("correlation_title", models.CharField(max_length=50)),
                ("active", models.BooleanField(default=True)),
                (
                    "project_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="mapping.MappingProject",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="mappingrule",
            name="mapcorrelation_type",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="mapping.MappingCorrelation",
            ),
        ),
    ]
