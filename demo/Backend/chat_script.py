import openai
import os
import json
import uuid
from datetime import datetime
from django.http import JsonResponse

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = "https://brainstorm-ai-openai.openai.azure.com/openai/deployments/gpt-4-ai-model/chat/completions?api-version=2025-01-01-preview"
AZURE_OPENAI_KEY = ""
AZURE_DEPLOYMENT_NAME = "gpt-4-ai-model"
AZURE_API_VERSION = "2025-01-01-preview"

# Configure OpenAI client for Azure
client = openai.AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_API_VERSION,
)

# Directory to store conversation history
CHAT_HISTORY_DIR = "chat_sessions"
if not os.path.exists(CHAT_HISTORY_DIR):
    os.makedirs(CHAT_HISTORY_DIR)

# Load chat history
def load_chat_history(session_id):
    session_file = os.path.join(CHAT_HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(session_file):
        with open(session_file, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

# Save chat history
def save_chat_history(session_id, chat_history):
    session_file = os.path.join(CHAT_HISTORY_DIR, f"{session_id}.json")
    with open(session_file, "w", encoding="utf-8") as file:
        json.dump(chat_history, file, indent=4)

# Generate a unique session ID
def generate_session_id():
    return str(uuid.uuid4())




def showSessions(message):
    sess_names = os.listdir("/home/a940623/GIEPETTO/demo/chat_sessions")
    return{
        "sessionNames":sess_names
    }

def formatSessionPayload(Sessid):
    htmlDOMText=""
    sessionToRetrive = "./chat_sessions/"+Sessid+".json"
    with open(sessionToRetrive, 'r') as file:
        data = json.load(file)
    for wiadomosc in data:
        htmlDOMText+='<p><strong>'+wiadomosc["role"]+':</strong>'+wiadomosc["content"]+'</p>'+'<br>'
    print(htmlDOMText)
    return{
        "ChatHistory":htmlDOMText
    }



def chat(message, session_id=None):
    if session_id is None:
        session_id = generate_session_id()
    
    chat_history = load_chat_history(session_id)
    chat_history.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,
        messages=[{"role": "system", "content": 'You are a helpful AI assistant, style the text with html tags, use <br>, emotes and colours'}] + chat_history,
        max_tokens=1000
    )#
    
    ai_message = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": ai_message})
    save_chat_history(session_id, chat_history)
    print(ai_message)
    return {
        "session_id": session_id,
        "user_message": message,
        "ai_message": ai_message,
        "chat_history": chat_history
    }
    
