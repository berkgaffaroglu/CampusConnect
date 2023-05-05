from django.db import models
from django.contrib.auth.models import User
from events.models import Event
from social_clubs.models import SocialClub
from PIL import Image
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from events.models import EventHeart 

# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField() 
    ambassador = models.BooleanField(default=False, null=True)
    new_notification_count = models.IntegerField(default=0, null=True, blank=True)
    dont_recommend_events = models.ManyToManyField(Event, related_name="events_dont_recommend", blank=True, default=None)
    
    def __str__(self):
        return self.user.username

    # resizing images
    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)

        if img.height > 100 or img.width > 100:
            new_img = (100, 100)
            img.thumbnail(new_img)
            img.save(self.avatar.path)
    def liked_events(self):
        liked = [x.event.pk for x in EventHeart.objects.filter(user=self.user).all()]
        querset = Event.objects.filter(id__in=liked)
        
        return querset



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.TextField(default="", null=True)
    description = models.TextField(default="", null=True)
    url = models.TextField(default="", null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='notification_event', null=True, default=None)
    club = models.ForeignKey(SocialClub, on_delete=models.CASCADE, related_name='notification_club', null=True, default=None)
    created_time = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        super().save()
        self.user.profile.new_notification_count += 1
        self.user.save()
        # Send email
        email = True
        if email:
            email = self.user.email
            # email = "berkgaffaroglu@gmail.com"

            if self.url:
                CURRENT_URL = settings.URL + self.url
                html_content = f"\n {self.description.capitalize()}. Please check out more on <a href='{CURRENT_URL}'>here</a>!"
            else:
                html_content = f"\n {self.description.capitalize()}"
            
            msg = EmailMultiAlternatives(self.title.title(), html_content,"campusconnectuskudar@gmail.com",[email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
