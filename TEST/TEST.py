import openai
import os
import json
import uuid
from datetime import datetime

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = "https://eviden-intern-openai-demo.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2025-01-01-preview"  # Replace with your actual endpoint
AZURE_OPENAI_KEY = "klucz"  # Replace with your actual API key
AZURE_DEPLOYMENT_NAME = "gpt-4o-mini"  # The model deployment name from Azure
AZURE_API_VERSION = "2023-12-01-preview"  # Update based on your Azure API version

# Configure OpenAI client for Azure
client = openai.AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_API_VERSION,
)

# Directory to store conversation history by session
CHAT_HISTORY_DIR = "chat_sessions"

# Create the directory if it doesn't exist
if not os.path.exists(CHAT_HISTORY_DIR):
    os.makedirs(CHAT_HISTORY_DIR)

# Generate a unique session ID
def generate_session_id():
    return str(uuid.uuid4())

# Load chat history for a specific session
def load_chat_history(session_id):
    session_file = os.path.join(CHAT_HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(session_file):
        with open(session_file, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return []

# Save chat history for a specific session
def save_chat_history(session_id, chat_history):
    session_file = os.path.join(CHAT_HISTORY_DIR, f"{session_id}.json")
    with open(session_file, "w", encoding="utf-8") as file:
        json.dump(chat_history, file, indent=4)

def chat_with_ai(user_input, session_id):
    # Load existing history for this session
    chat_history = load_chat_history(session_id)
    
    # Append user input to the history
    chat_history.append({"role": "user", "content": user_input})
    
    # Call OpenAI API to get AI's response
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,  # Model deployment name
        messages=[{"role": "system", "content": "You are a helpful AI assistant."}] + chat_history,
        max_tokens=100
    )
    
    ai_message = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": ai_message})
    
    # Save the updated chat history
    save_chat_history(session_id, chat_history)
    
    return ai_message

if __name__ == "__main__":
    print("AI Assistant: Hello! You can start chatting with me. Type 'exit' to end the conversation.")
    
    # Generate a new session ID
    session_id = generate_session_id()
    
    print(f"Session ID: {session_id}")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("AI Assistant: Goodbye!")
            break
        ai_response = chat_with_ai(user_input, session_id)
        print("AI:", ai_response)
