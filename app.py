from flask import *
import sys
import spotipy
import spotipy.util as util
from spotipy import oauth2
from config import *
from SpotifyController import SpotifyController
app = Flask(__name__)

token = ""
spc = SpotifyController("wheredidwego")

# sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, state=None, scope="user-top-read", cache_path=cache, proxies=None)

@app.route('/')
def index():
    print(spc.get_currently_playing())
    print(spc.get_top_artists())
    print(spc.get_top_tracks())
    return render_template("index.html", name=spc.username)

@app.route('/callback')
def callback():
    return redirect('/')


if __name__ == '__main__':
    app.run(port=3000)

