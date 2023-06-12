from django import template
from social_clubs.models import SocialClub
from events.models import EventHeart
from events.models import Event
from django.contrib.auth import user_logged_in

register = template.Library()

@register.filter
def sort_and_slice(notifications, count):
    if count > 5:
        count = 5
    return notifications.order_by("-created_time")[:count]


@register.filter
def is_manager(user):
    all_managers = [x.managers.all() for x in SocialClub.objects.all()]
    # print(all_managers)
    for i in all_managers:
        for j in i:
            if user == j:
                return True
    
    return False

@register.filter
def is_liked(event, user):
    is_liked = len(EventHeart.objects.filter(event=event, user=user))==0
    return is_liked