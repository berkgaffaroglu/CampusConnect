from django.urls import path
from .views import social_clubs, club_detail, search_clubs

urlpatterns = [
    path('social-clubs/', social_clubs, name='social-clubs'),
    path('club-detail/<int:pk>', club_detail, name='club-detail'),
    path('search-clubs/', search_clubs, name='search-clubs'),
]
