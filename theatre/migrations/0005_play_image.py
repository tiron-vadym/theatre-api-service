# Generated by Django 5.0.3 on 2024-03-11 23:55

import theatre.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "theatre",
            "0004_alter_ticket_options_alter_performance_theatre_hall_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="play",
            name="image",
            field=models.ImageField(
                null=True, upload_to=theatre.models.play_image_file_path
            ),
        ),
    ]