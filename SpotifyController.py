from flask import Flask
import sys
import spotipy
import spotipy.util as util
from config import *

GENRES = ["jazz", "rock", "indie", "classical", "pop", "soul", "latin", "hip hop", "rap", "folk", "acoustic", "metal", "funk", "electronic"]
RANGES = {
    'danceability' : 1,
    'loudness' : 60,
    'speechiness' : 1,
    'acousticness' : 1,
    'instrumentalness' : 1,
    'energy' : 1,
    'tempo' : 225,
    'valence' : 1
}
USER_FEATURES = ['danceability', 'loudness', 'speechiness', 'acousticness','instrumentalness', 'energy','tempo', "valence"]


class SpotifyController:

    def authenticate(self, username):
        self.username = username
        token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
        print(token)
        if token:
            self.sp = spotipy.Spotify(token)
            self.sp = spotipy.Spotify(token)

            return 1
        else:
            print("Can't get token for", username)
            return 0

    def authenticate_token(self, token):
        print(token)
        if token:
            self.sp = spotipy.Spotify(token)
            self.user_profile = self.get_current_user_music_profile()
            return 1
        else:
            print("Error")
            return 0


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

        tracks = self.get_track_list_features(top_tracks, ['danceability', 'loudness', 'speechiness', 'acousticness','instrumentalness', 'energy','tempo', 'valence'])
        genres = self.get_artist_list_features(top_artists)

        self.avg_features = tracks
        self.top_genres = genres

        return [tracks, genres]

    def get_track_list_features(self, tracks, keys):
        avg_features = {}
        for x in keys:
            avg_features[x] = 0.0
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
        for x in GENRES:
            genres[x] = 0

        for x in artists:
            for g in x['genres']:
                temp = list(filter(lambda x: x in g, GENRES))
                for g in temp:
                    genres[g] += 1
        return genres.items()

    def user_playlist_tracks(self, playlist_id=None, fields=None,
                             limit=100, offset=0, market=None):
        ''' Get full details of the tracks of a playlist owned by a user.

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - fields - which fields to return
                - limit - the maximum number of tracks to return
                - offset - the index of the first track to return
                - market - an ISO 3166-1 alpha-2 country code.
        '''
        plid = self.sp._get_id('playlist', playlist_id)
        return self.sp._get("playlists/%s/tracks" % (plid),
                         limit=limit, offset=offset, fields=fields,
                         market=market)


    def get_playlist_features(self, playlist, features):
        tracks = [x['track'] for x in self.user_playlist_tracks(playlist,limit=30)['items']]
        track_ids = [x['id'] for x in tracks]
        track_features = self.get_track_list_features(track_ids, features)
        return track_features

    def get_playlist_artists(self, playlist):
        tracks = [x['track'] for x in self.user_playlist_tracks(playlist, limit=30)['items']]
        print(tracks)
        artists_list = [x['album']['artists'] for x in tracks]

        artists = {}
        for x in artists_list:
            for y in x:
                if(y['id'] != "0LyfQWJT6nXafLPZqxe9Of"):
                    if y['name'] in artists:
                        artists[y['name']] += 1
                    else:
                        artists[y['name']] = 1

        return artists

    def get_playlist_artist_objects(self, playlist):
        tracks = [x['track'] for x in self.user_playlist_tracks(playlist, limit=30)['items']]
        print(tracks)
        artists_list = [x['album']['artists'] for x in tracks]

        artists = []
        for x in artists_list:
            for y in x:
                if(y['id'] != "0LyfQWJT6nXafLPZqxe9Of"):
                    if not y['name'] in artists:
                        artists.append(y)
        return artists

    def get_playlist_genres(self, playlist):

        artists = self.get_playlist_artist_objects(playlist)
        print(artists)
        artist_objects = []
        for x in artists:
            a = self.sp.artist(x['id'])
            if (a != []):
                artist_objects.append(a)

        print(artist_objects)

        genres = self.get_artist_list_features(artist_objects)

        return genres

    def score(self, id, playlist_features, filters):
        track_score = 0
        genre_score = 0


        genres = self.get_playlist_genres(id)

        n = sum(map(lambda x:x[1], genres)) * 1.0

        for filter in filters:
            track_score += (1-(abs(self.avg_features[filter]-playlist_features[filter]))/RANGES[filter])*100/len(filters)

        vals1 = list(dict(self.top_genres).values())
        vals2 = list(dict(genres).values())
        for i in range(0, len(genres)):
            genre_score += min(vals1[i],vals2[i])


        return genre_score/n * .25 + track_score * .75