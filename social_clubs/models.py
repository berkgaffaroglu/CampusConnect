from django.db import models
from django.contrib.auth.models import User

class SocialClub(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    members = models.ManyToManyField(User, related_name='clubs_joined')
    managers = models.ManyToManyField(User, related_name='admin_of')
    def __str__(self):
        return self.name
    

class SocialClubImage(models.Model):
    social_club = models.ForeignKey(SocialClub, on_delete=models.CASCADE, related_name='social_club_images')
    image = models.ImageField(upload_to='social_club_images/')
    def delete(self):
        try:
            self.image.delete()
            super().delete()
        except:
            pass

