
# used to access environment variables securely (sensitive data)
from email.quoprimime import body_check
import os

# used to encode strings into bytes and back
import base64

# used to convert JSON data into strings
import json
import requests
import time


# TODO: get auth token from client
token_request_url = "https://accounts.spotify.com/api/token"

CLIENT_ID = 'e7dd4d704dbf462da4d1bb541f55695f'
CLIENT_SECRET = '07bc8202e8404f7e82df0d49a7128129'

# encode credentials into bytes, then decode into a string for the HTTP POST request to Spotify to authenticate
BASE64_ENCODED_HEADER_STRING = base64.b64encode(bytes(f"{CLIENT_ID}:{CLIENT_SECRET}", "ISO-8859-1")).decode("ascii")

#initializing dictionaries for HTTP POST request
headers = {}
data = {}

headers['Authorization'] = f"Basic {BASE64_ENCODED_HEADER_STRING}"

data['grant_type'] = "client_credentials"
data['json'] = True
data['scope'] = ['user-read-recently-played', 'user-modify-playback-state', 'user-read-playback-position', 'app-remote-control', 'user-read-playback-state', 'playlist-read-private']

r = requests.post(url=token_request_url, headers=headers, data=data)
  
token = r.json()['access_token']
print(token)

headers = {
    'Authorization': 'Bearer {token}'.format(token=token)
}


BASE_URL = 'https://api.spotify.com/v1/'



def getLoudestSection(track_id, auth):
    print(track_id)
    r = requests.get(BASE_URL + 'audio-analysis/' + track_id, headers=auth)

    r = r.json()

    #print(json.dumps(r['segments'], indent=2))

    segments = r['sections']

    loudest_section = max(segments, key = lambda x: x['loudness'])

    return [loudest_section['start'], loudest_section['duration']]



def playTrack(context_uri, section, pos, auth):

    dat= {
    "context_uri": context_uri,
    "offset": {'position': pos},
    "position_ms": int(section[0]*1000)
    }

    r = requests.put('https://api.spotify.com/v1/me/player/play', data=json.dumps(dat), headers=auth)
    time.sleep(min(section[1], 25))
    r = requests.put('https://api.spotify.com/v1/me/player/pause', headers=auth)



def getTrackIds(playlistId, auth):
    r = requests.get('https://api.spotify.com/v1/playlists/{}'.format(playlistId), headers=auth)
    r = r.json()
    trackIds = []
    for t in r['tracks']['items']:
        trackIds.append(t['track']['id'])
    return trackIds


def getTracks(playlistId, auth):
    r = requests.get('https://api.spotify.com/v1/playlists/{}'.format(playlistId), headers=auth)
    r = r.json()
    tracks = []
    for t in r['tracks']['items']:
        tracks.append(t['track'])

    return tracks


def playTracks(trackIds, playlistId, auth):
    for i in range(len(trackIds)):
        s = getLoudestSection(trackIds[i], auth)
        print(s)
        #r = requests.post('https://adaptatune.herokuapp.com/')
        playTrack('spotify:playlist:{}'.format(playlistId), s, i, auth)

    
def nextTrack(auth):
    r = requests.post('https://api.spotify.com/v1/me/player/next', headers=auth)


def playSingleTrack(playlistId, trackId, auth, pos):
    s = getLoudestSection(trackId, auth)
    playTrack('spotify:playlist:{}'.format(playlistId), s, pos, auth)


if __name__ == "__main__":
    playTracks()


