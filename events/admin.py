from django.contrib import admin
from .models import Event,EventImage,EventComment,EventHeart

# Register your models here.
admin.site.register(Event)
admin.site.register(EventImage)
admin.site.register(EventComment)
admin.site.register(EventHeart)