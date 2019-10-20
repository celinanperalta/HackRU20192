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
        results = self.sp.current_user_top_artists(50, 0, "medium_term")
        return [x for x in results['items']]

    def get_top_tracks(self):
        results = self.sp.current_user_top_tracks(50, 0, "medium_term")
        return [x['id'] for x in results['items']]

    def get_current_user_music_profile(self):
        top_tracks = self.get_top_tracks()
        top_artists = self.get_top_artists()

        tracks = self.get_track_list_features(top_tracks)
        genres = self.get_artist_list_features(top_artists)

        return [tracks, genres]

    def get_track_list_features(self, tracks):
        keys = ['danceability', 'loudness', 'speechiness', 'acousticness','instrumentalness', 'energy','tempo']
        avg_features = {
            'danceability' : 0.0,
            'loudness': 0.0,
            'speechiness': 0.0,
            'acousticness' : 0.0,
            'instrumentalness' : 0.0,
            'energy': 0.0,
            'tempo' : 0.0
        }
        features = self.sp.audio_features(tracks)
        for arr in features:
            for x in keys:
                avg_features[x] += arr[x]
        for x in avg_features:
            avg_features[x] /= len(tracks)
        return avg_features

    #takes a list of artist objects, not ids
    def get_artist_list_features(self, artists):
        genres = {}
        for x in artists:
            for g in x['genres']:
                if g in genres:
                    genres[g] += 1
                else:
                    genres[g] = 1
        return genres
