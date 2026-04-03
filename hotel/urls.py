from django.urls import path

from .views import assistant_chat, home

urlpatterns = [
    path("", home, name="home"),
    path("assistant/chat/", assistant_chat, name="assistant_chat"),
]
