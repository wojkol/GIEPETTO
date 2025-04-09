from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from .chat_script import chat  
from .chat_script import showSessions
from .chat_script import formatSessionPayload
from .chat_script import authenticate_spotify,get_spotify_token,get_spotify_client, get_playlists

@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "")
            session_id = data.get("session_id", None)
            response_data = chat(message, session_id)
            return JsonResponse(response_data)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

#pokazywanie sesji
@csrf_exempt
def showSessions_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "")
            response_data = showSessions(message)
           
            return JsonResponse(response_data)
        
        #errorhandling
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def formatSessionPayload_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "")
            response_data = formatSessionPayload(message)
            return JsonResponse(response_data)
        
        #errorhandling
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)





#spotify views
@csrf_exempt
def login(request):
    # Redirect user to Spotify login page
    auth_url = authenticate_spotify()
    return redirect(auth_url)
@csrf_exempt
def callback(request):
    # Handle the callback after user authorizes the app
    if 'code' not in request.GET:
        return HttpResponse("Error: No authorization code found.", status=400)
    
    access_token = get_spotify_token(request)
    # Save the access token somewhere, like the session
    request.session['spotify_access_token'] = access_token
    os.makedirs(os.path.dirname("./token.json"), exist_ok=True)
    with open("./token.json", 'w') as f:
        json.dump(access_token, f)
    return redirect('http://127.0.0.1:8000') # Redirect to some other view after successful auth

@csrf_exempt
def get_playlists_view(request):
    access_token = request.session.get('spotify_access_token')
    if not access_token:
        return redirect('login')
    sp = get_spotify_client(access_token)

    if request.method == "POST":
        try:
            response_data =get_playlists(sp)
            return JsonResponse(response_data)
        
        #errorhandling
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)