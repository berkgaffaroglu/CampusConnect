# Generated by Django 4.1.2 on 2023-04-16 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social_clubs', '0002_socialclub_managers'),
        ('events', '0013_event_social_club'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='social_club',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='club_events', to='social_clubs.socialclub'),
        ),
    ]