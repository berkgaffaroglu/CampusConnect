# Generated by Django 4.1.2 on 2023-04-29 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0021_eventcomment_created_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='dislikes',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='likes',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
