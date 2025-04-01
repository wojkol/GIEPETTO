import openai
import os
import json

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

# File to store conversation history
CHAT_HISTORY_FILE = "chat_history.json"

# Load chat history from file
if os.path.exists(CHAT_HISTORY_FILE):
    with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as file:
        chat_history = json.load(file)
else:
    chat_history = []

def chat_with_ai(user_input):
    chat_history.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,  # Model deployment name
        messages=[{"role": "system", "content": "You are a helpful AI assistant."}] + chat_history,
        max_tokens=100
    )
    
    ai_message = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": ai_message})
    
    # Save chat history to file
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(chat_history, file, indent=4)
    
    return ai_message

if __name__ == "__main__":
    print("AI Assistant: Hello! You can start chatting with me. Type 'exit' to end the conversation.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("AI Assistant: Goodbye!")
            break
        ai_response = chat_with_ai(user_input)
        print("AI:", ai_response)
