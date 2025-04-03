



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .chat_script import chat  # Import chat function from the script

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
