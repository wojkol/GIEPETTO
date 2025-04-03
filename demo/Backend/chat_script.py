import openai
import os
import json
import uuid
from datetime import datetime

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = "https://eviden-intern-openai-demo.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2025-01-01-preview"
AZURE_OPENAI_KEY = "6ufNTtmfS6v8nvBKqKiH3pnIbzddOchNaaMgnPzKmpb7JKrnhWkoJQQJ99BCACYeBjFXJ3w3AAABACOGeSxR"
AZURE_DEPLOYMENT_NAME = "gpt-4o-mini"
AZURE_API_VERSION = "2023-12-01-preview"

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

# Chat function for Django
def chat(message, session_id=None):
    if session_id is None:
        session_id = generate_session_id()
    
    chat_history = load_chat_history(session_id)
    chat_history.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,
        messages=[{"role": "system", "content": "You are a helpful AI assistant."}] + chat_history,
        max_tokens=100
    )
    
    ai_message = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": ai_message})
    save_chat_history(session_id, chat_history)
    
    return {
        "session_id": session_id,
        "user_message": message,
        "ai_message": ai_message,
        "chat_history": chat_history
    }
print(chat("and what about lesotho","e969d35f-a296-4c84-8bb4-bb88dc34ba89"))