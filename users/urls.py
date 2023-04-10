from django.urls import path
from .views import home, profile, edit_profile, RegisterView

urlpatterns = [
    path('', home, name='users-home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/<int:pk>/', profile, name='users-profile'),
    path('edit-profile/<int:pk>/', edit_profile, name='edit-profile'),
]
