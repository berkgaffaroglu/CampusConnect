from django.urls import path
from .views import events, event_detail, my_events, create_event, delete_event,edit_event

urlpatterns = [
    path('events/', events, name='events'),
    path('event/<int:pk>/', event_detail, name='event-detail'),
    path('my-events/', my_events , name='my-events'),
    path('create-event/', create_event, name='create-event'),
    path('edit-event/<int:pk>/', edit_event, name='edit-event'),
    path('delete-event/<int:pk>/', delete_event, name='delete-event'),
]
