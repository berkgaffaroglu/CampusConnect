# Generated by Django 4.1.2 on 2023-04-11 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_alter_event_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_past',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]