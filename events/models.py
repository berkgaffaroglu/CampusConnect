from django.db import models
import pytz
from django.contrib.auth.models import User
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone

def validate_datetime(value):
    return
    
class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.TextField()
    price = models.FloatField(blank=True, default=0)
    time = models.DateTimeField(validators=[validate_datetime])
    users = models.ManyToManyField(User, related_name='events_attending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', blank=True, default="", null=True)
    is_past = models.BooleanField(blank=True, default=False)
    def __str__(self):
        return self.title
    def is_past(self):
        if self.time < timezone.now():
            return True
        return False