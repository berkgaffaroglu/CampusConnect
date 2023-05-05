# Generated by Django 4.1.2 on 2023-04-30 00:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0026_rename_eventhearts_eventheart'),
        ('social_clubs', '0003_socialclubimage'),
        ('users', '0012_alter_profile_dont_recommend_events'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='club',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_club', to='social_clubs.socialclub'),
        ),
        migrations.AddField(
            model_name='notification',
            name='event',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_event', to='events.event'),
        ),
    ]
