# Generated by Django 4.1.2 on 2023-04-26 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_notification_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]