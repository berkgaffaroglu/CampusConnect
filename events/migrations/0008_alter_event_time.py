# Generated by Django 4.1.2 on 2023-04-11 03:09

from django.db import migrations, models
import events.models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_alter_event_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.DateTimeField(validators=[events.models.validate_datetime]),
        ),
    ]
