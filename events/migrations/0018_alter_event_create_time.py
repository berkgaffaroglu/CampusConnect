# Generated by Django 4.1.2 on 2023-04-26 00:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0017_event_create_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 26, 0, 17, 57, 835340, tzinfo=datetime.timezone.utc)),
        ),
    ]