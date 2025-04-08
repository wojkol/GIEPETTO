


from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .chat_script import chat  
from .chat_script import showSessions
from .chat_script import formatSessionPayload


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