# Generated by Django 2.2.6 on 2019-10-29 11:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("mapping", "0042_mappingprogressrecord_project"),
    ]

    operations = [
        migrations.AddField(
            model_name="mappingeventlog",
            name="action_user",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="event_action_user",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
