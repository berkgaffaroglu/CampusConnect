from django.urls import path
from .views import liked_events, dont_recommend_events, events, event_detail, create_event, delete_event,edit_event, delete_comment, toggle_recommend_event,toggle_like_event, my_events, search

urlpatterns = [
    path('events/', events, name='events'),
    path('liked-events/<int:pk>/', liked_events, name='liked-events'),
    path('dont-recommend-events/<int:pk>/', dont_recommend_events, name='dont-recommend-events'),
    path('event/<int:pk>/', event_detail, name='event-detail'),
    path('my-events/', my_events, name='my-events'),
    path('search/', search, name='search'),

    path('create-event/', create_event, name='create-event'),
    path('edit-event/<int:pk>/', edit_event, name='edit-event'),
    path('delete-event/<int:pk>/', delete_event, name='delete-event'),
    path('delete-comment/<int:pk>/', delete_comment, name='delete-comment'),
    path('toggle-recommend-event/<int:pk>/<str:detail>/', toggle_recommend_event, name='toggle-recommend-event'),
    path('toggle-like-event/<int:pk>/', toggle_like_event, name='toggle-like-event'),
]
