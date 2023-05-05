# Generated by Django 4.1.2 on 2023-04-29 01:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0022_event_dislikes_event_likes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='dislikes',
        ),
        migrations.RemoveField(
            model_name='event',
            name='likes',
        ),
        migrations.CreateModel(
            name='EventHearts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('likes', models.IntegerField(blank=True, default=0, null=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes_events', to='events.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_likes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]