# Generated by Django 4.1.2 on 2023-04-09 23:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0005_event_price_alter_event_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='created_by',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, related_name='created_events', null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
