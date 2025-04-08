from django.urls import path
from django.shortcuts import render

def index(request):
    return render(request, "index.html")  # Load the HTML template

urlpatterns = [
    path("", index, name="index"),
]
