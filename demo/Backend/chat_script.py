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
            historyDOM.append('<p><strong>'+wiadomosc["role"]+':</strong>'+'<br>'+wiadomosc["content"]+'</p>')
    return{
        "ChatHistory":historyDOM
    }





#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#chat implementation

functions = [
    {
    "name": "search",
    "description": "Search for songs in the Spotify API. Can execute multiple queries at once for multiple songs, returning info about a given number of top results from each query.Dont return album covers if not specified .USE ONLY WHEN USER STATED TO USE SPOTIFY",
    "parameters": {
        "type": "object",
        "properties": {
            "querys": {
                "type": "array",
                "description": "List of queries for the Spotify API to search for.",
                "items": {
                    "type": "string"
                }
            },
            "resultCount": {
                "type": "integer",
                "description": "How many top results each query should return."
            }
        },
        "required": ["querys", "resultCount"]
    }
    },
    {
    "name": "get_user_playlists",
    "description": "Returns info about playlists of the current user",
    "parameters": {
        "type": "object",
        "properties": {}
    }
    },
    {
    "name": "add_tracks_to_playlist",
    "description": "Add tracks to spotify playlists, use only if user previously asked to retrieve spotify playlist info and track info",
    "parameters": {
        "type": "object",
        "properties": {
            "track_ids": {
                "type": "array",
                "description": "list of IDs of tracks that are to be added",
                "items": {
                    "type": "string"
                }
            },
            "playlist_id": {
                "type": "string",
                "description": "ID of target Playlist"
            }
        },
        "required": ["track_ids", "playlist_id"]
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
        if(response.choices[0].message.function_call.name=="search"):
            args = json.loads(response.choices[0].message.function_call.arguments)
            chat_history.append({"role": "system", "content": ("assistant searched for tracks, function returned:"+  json.dumps(search(args["querys"],args["resultCount"])))})
            afterFunctionresponse = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=[{"role": "system", "content": 'You are a helpful, witty AI assistant '}] + chat_history,
            max_tokens=1000,
            functions=functions,
            function_call="auto"
            )
            ai_message = afterFunctionresponse.choices[0].message.content
        if(response.choices[0].message.function_call.name=="get_user_playlists"):
            chat_history.append({"role": "system", "content": ("assistant requested playlist info, function returned:"+  json.dumps(get_user_playlists()))})
            afterFunctionresponse = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=[{"role": "system", "content": 'You are a helpful, witty AI assistant '}] + chat_history,
            max_tokens=1000,
            functions=functions,
            function_call="auto"
            )
            ai_message = afterFunctionresponse.choices[0].message.content
        if(response.choices[0].message.function_call.name=="add_tracks_to_playlist"):
            args = json.loads(response.choices[0].message.function_call.arguments)
            chat_history.append({"role": "system", "content": "asistand added added tracks to playlist:"})
            add_tracks_to_playlist(args["playlist_id"],args["track_ids"])
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
       scope="user-library-read playlist-read-private playlist-modify-public playlist-modify-private"
    )
    
    # Redirect the user to Spotify's authentication page
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

def get_spotify_token(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-library-read playlist-read-private playlist-modify-public playlist-modify-private"
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

def search(querys,resultCount):
    payload = {}
    sp = ''
    with open("./token.json", 'r') as f:
        sp =  json.load(f)
    sp = Spotify(auth=sp)
    for query in querys:
        resultnumber = 1
        payload[query]=[]
        result = sp.search(q=query, type='track', limit=resultCount)
        tracks = result.get('tracks', {}).get('items', [])
        if not tracks:
            return None
        for track in tracks:
            payload[query].append({
            'result': resultnumber,
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'preview_url': track['preview_url'],
            'spotify_url': track['external_urls']['spotify'],
            'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'id': track['id']
            })
            resultnumber+=1
    return payload

def get_user_playlists():
    sp = ''
    with open("./token.json", 'r') as f:
        sp =  json.load(f)
    sp = Spotify(auth=sp)
    playlists = []
    results = sp.current_user_playlists(limit=50)
    # Spotify paginates results, so keep fetching until done
    while results:
        for item in results['items']:
            playlists.append({
                'name': item['name'],
                'id': item['id'],
                'tracks_total': item['tracks']['total'],
                'public': item['public'],
                'collaborative': item['collaborative'],
                'description': item['description'],
                'spotify_url': item['external_urls']['spotify'],
                'image': item['images'][0]['url'] if item['images'] else None
            })

        # Check if there's a next page
        if results['next']:
            results = sp.next(results)
        else:
            break

    return playlists

def add_tracks_to_playlist( playlist_id: str, track_ids: list):
    sp = ''
    with open("./token.json", 'r') as f:
        sp =  json.load(f)
    sp = Spotify(auth=sp)

    # Spotify API allows a max of 100 tracks per request
    batch_size = 100
    responses = []

    for i in range(0, len(track_ids), batch_size):
        batch = track_ids[i:i+batch_size]
        response = sp.playlist_add_items(playlist_id, batch)
        responses.append(response)

    return responses
