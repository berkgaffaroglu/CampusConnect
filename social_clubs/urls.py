from django.urls import path
from .views import social_clubs, club_detail, create_club, edit_club, delete_club, my_clubs

urlpatterns = [
    path('social-clubs/', social_clubs, name='social-clubs'),
    path('my-clubs/', my_clubs, name='my-clubs'),
    path('club-detail/<int:pk>', club_detail, name='club-detail'),
    path('create-club/', create_club, name='create-club'),
    path('edit-club/<int:pk>/', edit_club, name='edit-club'),
    path('delete-club/<int:pk>/', delete_club, name='delete-club'),
]
