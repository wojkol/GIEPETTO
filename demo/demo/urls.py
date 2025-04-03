from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("Frontend.urls")),  # Load frontend (for rendering index.html)
    path("api/", include("Backend.urls")),  # Load backend (API endpoints)
]
