from django.urls import path
from .views import chat_view

urlpatterns = [
    path("chat/", chat_view, name="chat_api"),  # API endpoint for chatting
]
