from flask import *
import sys
import spotipy
import spotipy.util as util
from spotipy import oauth2
from config import *

app = Flask(__name__)

token = ""

sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, "user-top-read", cache)

@app.route('/')
def index():
    access_token = ""

    token_info = sp_oauth.get_cached_token()
    print(token_info)

    if token_info:
        print ("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code:
            print ("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        print ("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)
        results = sp.current_user()
        return results

    else:
        return htmlForLoginButton()

@app.route('/callback')
def callback():
    print("ajkdfhf")
    if token:
        sp = spotipy.Spotify(token)
        # results = sp._get('me/player/currently-playing')
        # song = results['item']['artists'][0]['name'] + " - " + results['item']['name']
    return redirect('/')

@app.route('/login')
def login():
    pass

def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


if __name__ == '__main__':
    app.run(port=3000)

