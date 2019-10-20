from flask import Flask
import sys
import spotipy
import spotipy.util as util
from config import *



def get_api(username):
    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
    if token:
        return spotipy.Spotify(token)
    else:
        print("Can't get token for", username)

def get_currently_playing(self):
    results = self.sp._get('me/player/currently-playing')
    return results['item']['artists'][0]['name'] + " - " + results['item']['name']