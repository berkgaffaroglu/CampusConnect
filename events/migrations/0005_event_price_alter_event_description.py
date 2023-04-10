# Generated by Django 4.1.2 on 2023-04-05 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_alter_event_description_alter_event_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='price',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
