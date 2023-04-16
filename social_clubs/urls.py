from django.urls import path
from .views import socail_clubs, club_detail

urlpatterns = [
    path('social-clubs/', socail_clubs, name='social-clubs'),
    path('club-detail/<int:pk>', club_detail, name='club_detail'),
]
