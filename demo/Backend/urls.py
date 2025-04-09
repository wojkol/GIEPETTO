from django.urls import path
from .views import chat_view
from .views import showSessions_view
from .views import login, callback, formatSessionPayload_view,get_playlists_view


urlpatterns = [
    path("chat/", chat_view, name="chat_api"),
    path("sessions/", showSessions_view, name="showin_sessions_for_api" ),
    path("loadFormatedSessions/", formatSessionPayload_view,name="needed for session retrieval"),
    path('login/', login, name='login'),
    path('callback/', callback, name='callback'),
    path('playlists/', get_playlists_view, name='getting playlists'),
    ]
