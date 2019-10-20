from flask import Flask
import sys
import spotipy
import spotipy.util as util
from config import *

class SpotifyController:


    def authenticate(self, username):
        self.username = username
        token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
        print(token)
        if token:
            self.sp = spotipy.Spotify(token)
        else:
            print("Can't get token for", username)

    def get_api(self):
        return self.sp

    def get_currently_playing(self):
        results = self.sp._get('me/player/currently-playing')
        return results['item']['artists'][0]['name'] + " - " + results['item']['name']

    def get_top_artists(self):
        results = self.sp.current_user_top_artists(20, 0, "medium_term")
        return [x['name'] for x in results['items']]

    def get_top_tracks(self):
        results = self.sp.current_user_top_tracks(20, 0, "medium_term")
        return [x['name'] for x in results['items']]

    def get_track_list_features(self, tracks):
        pass

    def get_artist_list_features(self,artists):
        pass
