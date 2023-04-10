from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.TextField()
    price = models.FloatField(blank=True, default=0)
    time = models.DateTimeField()
    users = models.ManyToManyField(User, related_name='events_attending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', blank=True, default="", null=True)
    def __str__(self):
        return self.title