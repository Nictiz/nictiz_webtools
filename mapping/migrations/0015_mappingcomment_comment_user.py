# Generated by Django 2.2.6 on 2019-10-19 12:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mapping", "0014_auto_20191019_1158"),
    ]

    operations = [
        migrations.AddField(
            model_name="mappingcomment",
            name="comment_user",
            field=models.TextField(default="mertens", max_length=500),
            preserve_default=False,
        ),
    ]
