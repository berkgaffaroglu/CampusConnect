from django.db import models
import pytz
from django.contrib.auth.models import User
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone
from social_clubs.models import SocialClub

    
class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.TextField()
    price = models.FloatField(blank=True, default=0)
    time = models.DateTimeField()
    users = models.ManyToManyField(User, related_name='events_attending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', blank=True, default="", null=True)
    maximum_people = models.IntegerField(blank=True, default=3)
    social_club = models.ForeignKey(SocialClub, on_delete=models.CASCADE, related_name='club_events',blank=True, default="", null=True)
    created_time = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.title
    def is_past(self):
        if self.time < timezone.now():
            return True
        else:
            return False
        
class EventHeart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_likes')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='likes_event')

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_images')
    image = models.ImageField(upload_to='event_images/')

class EventComment(models.Model):
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, related_name='reply_comments', blank=True, null=True)
    commentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_comments')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments_event')
    comment = models.TextField(blank=True)
    approved = False
    created_time = models.DateTimeField(auto_now_add=True, null=True)
    

