# Generated by Django 5.0.3 on 2024-03-10 14:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("theatre", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="play",
            name="actors",
            field=models.ManyToManyField(to="theatre.actor"),
        ),
        migrations.AddField(
            model_name="play",
            name="genres",
            field=models.ManyToManyField(to="theatre.genre"),
        ),
        migrations.AddField(
            model_name="ticket",
            name="reservation",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="theatre.reservation",
            ),
            preserve_default=False,
        ),
    ]
