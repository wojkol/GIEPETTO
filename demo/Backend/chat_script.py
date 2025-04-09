import openai
import os
import json
import uuid
from datetime import datetime
from django.http import JsonResponse
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from django.conf import settings
from spotipy import Spotify
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = "https://brainstorm-ai-openai.openai.azure.com/openai/deployments/gpt-4-ai-model/chat/completions?api-version=2025-01-01-preview"
AZURE_OPENAI_KEY = "1CKKDYaRC8zfGLvgggbZTW90POSliW4UMA4h2jVf3VTQHbqmBoy0JQQJ99BAACYeBjFXJ3w3AAABACOGCtqu"
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
    sess_names = os.listdir("/home/a940614/GIEPETTO/GIEPETTO/demo/chat_sessions")
    for name in sess_names:
        if(name[0:4]=="sess"):
            chat_history = load_chat_history(name[0:-5])
            #print(chat_history)
            response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=[{"role": "system", "content": 'Name our conversation up to this point, return max 6 WORDS'}] + chat_history,
            max_tokens=100
            )#
            newname = response.choices[0].message.content
            os.rename("/home/a940614/GIEPETTO/GIEPETTO/demo/chat_sessions/"+name, "/home/a940614/GIEPETTO/GIEPETTO/demo/chat_sessions/"+newname+".json")
    sess_names = os.listdir("/home/a940614/GIEPETTO/GIEPETTO/demo/chat_sessions")
    return{
        "sessionNames":sess_names
    }

def formatSessionPayload(Sessid):
    htmlDOMText=""
    historyDOM = []
    sessionToRetrive = "./chat_sessions/"+Sessid+".json"
    with open(sessionToRetrive, 'r') as file:
        data = json.load(file)
    for wiadomosc in data:
        if wiadomosc["role"]!="system":
            historyDOM.append('<p><strong>'+wiadomosc["role"]+':</strong>'+wiadomosc["content"]+'</p>')
    return{
        "ChatHistory":historyDOM
    }





#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#chat implementation

functions = [
    {
        "name": "search_track",
        "description": "Search for a song on Spotify and return information about the top result. IDs are used for adding tracks to playlists/my music",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "query for spotify api."
                }
            },
            "required": ["query"]
        }
    },
     {
        "name": "search_tracks",
        "description": "Search for 10 tracks on Spotify and return information about them. IDs are used for adding tracks to playlists/my music",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "query for spotify api"
                }
            },
            "required": ["query"]
        }
    }
]



def chat(message, session_id=None):
    if session_id is None:
        session_id = generate_session_id()
    
    chat_history = load_chat_history(session_id)
    chat_history.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,
        messages=[{"role": "system", "content": 'You are a helpful, witty AI assistant '}] + chat_history,
        max_tokens=1000,
        functions=functions,
        function_call="auto"
    )#
    ai_message = response.choices[0].message.content
    if(response.choices[0].finish_reason== "function_call"):
        #call function named search_tracks
        if(response.choices[0].message.function_call.name=="search_track"):
            query = response.choices[0].message.function_call.arguments[10:-2]
            chat_history.append({"role": "system", "content": ("assistant searched for tracks, function returned:"+  json.dumps(search_track(query)))})
            afterFunctionresponse = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=[{"role": "system", "content": 'You are a helpful, witty AI assistant '}] + chat_history,
            max_tokens=1000,
            functions=functions,
            function_call="auto"
            )
            ai_message = afterFunctionresponse.choices[0].message.content
        if(response.choices[0].message.function_call.name=="search_tracks"):
            query = response.choices[0].message.function_call.arguments[10:-2]
            chat_history.append({"role": "system", "content": ("assistant searched for tracks, function returned:"+  json.dumps(search_tracks(query)))})
            afterFunctionresponse = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=[{"role": "system", "content": 'You are a helpful, witty AI assistant '}] + chat_history,
            max_tokens=1000,
            functions=functions,
            function_call="auto"
            )
            ai_message = afterFunctionresponse.choices[0].message.content

    chat_history.append({"role": "assistant", "content": ai_message})
    save_chat_history(session_id, chat_history)
    #print(ai_message)
    #print(ai_message)
    return {
        "session_id": session_id,
        "user_message": message,
        "ai_message": ai_message,
        "chat_history": chat_history
    }

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#functions for spotify
def authenticate_spotify():
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-library-read playlist-read-private",
    )
    
    # Redirect the user to Spotify's authentication page
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

def get_spotify_token(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
    )
    
    # Get the token from the URL
    token_info = sp_oauth.get_access_token(request.GET['code'])
    return token_info['access_token']

def get_spotify_client(access_token):
    # Initialize Spotify client with the access token
    sp = spotipy.Spotify(auth=access_token)
    return sp

def get_playlists(sp):
    playlists = sp.current_user_playlists()
    responsedata=[]
    for idx, playlist in enumerate(playlists['items']):
        responsedata.append(f"{idx + 1}. {playlist['name']} - {playlist['tracks']['total']} tracks")
    return {"responsedata":responsedata}


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# functions for chat
def search_track(query: str):
    """
    Search for a track on Spotify and return the top result.
    
    :param query: The name of the track (or artist, album, etc.).
    :param access_token: A valid Spotify access token.
    :return: A dictionary with the top result's details or None if no result is found.
    """
    sp = ''
    with open("./token.json", 'r') as f:
        sp =  json.load(f)
    sp = Spotify(auth=sp)
    result = sp.search(q=query, type='track', limit=1)

    tracks = result.get('tracks', {}).get('items', [])
    if not tracks:
        return None

    top_track = tracks[0]
    return {
        'name': top_track['name'],
        'artist': top_track['artists'][0]['name'],
        'album': top_track['album']['name'],
        'preview_url': top_track['preview_url'],
        'spotify_url': top_track['external_urls']['spotify'],
        'image': top_track['album']['images'][0]['url'] if top_track['album']['images'] else None,
        'id': top_track['id']
    }

def search_tracks(query: str):
    """
    Search for tracks on Spotify and return the top 10 results.
    
    :param query: The name of the track (or artist, album, etc.).
    :param access_token: A valid Spotify access token.
    :return: A list of dictionaries containing details of the top 10 results.
    """
    with open("./token.json", 'r') as f:
        sp =  json.load(f)
    sp = Spotify(auth=sp)
    result = sp.search(q=query, type='track', limit=10)

    tracks = result.get('tracks', {}).get('items', [])
    if not tracks:
        return []

    track_results = []
    for track in tracks:
        track_results.append({
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'preview_url': track['preview_url'],
            'spotify_url': track['external_urls']['spotify'],
            'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'id': track['id']
        })

    return track_results

