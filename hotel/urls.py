from django.urls import path

from .views import assistant_chat, home, room_detail

urlpatterns = [
    path("", home, name="home"),
    path("room/<str:room_number>/", room_detail, name="room_detail"),
    path("assistant/chat/", assistant_chat, name="assistant_chat"),
]
