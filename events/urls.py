from django.urls import path
from .views import liked_events, dont_recommend_events, events, event_detail, create_event, delete_event,edit_event

urlpatterns = [
    path('events/', events, name='events'),
    path('liked-events/<int:pk>/', liked_events, name='liked-events'),
    path('dont-recommend-events/<int:pk>/', dont_recommend_events, name='dont-recommend-events'),
    path('event/<int:pk>/', event_detail, name='event-detail'),
    path('create-event/', create_event, name='create-event'),
    path('edit-event/<int:pk>/', edit_event, name='edit-event'),
    path('delete-event/<int:pk>/', delete_event, name='delete-event'),
    path('delete-event/<int:pk>/', delete_event, name='delete-event'),
]
