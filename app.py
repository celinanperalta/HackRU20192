from flask import *
import sys
import spotipy
import spotipy.util as util
from spotipy import oauth2
from config import *
from SpotifyController import SpotifyController
app = Flask(__name__)

token = ""
spc = SpotifyController()

# sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, state=None, scope="user-top-read", cache_path=cache, proxies=None)

@app.route('/')
def index():
    spc.authenticate("wheredidwego")
    return render_template("index.html")

@app.route('/login')
def login():
    pass

@app.route('/callback')
def callback():
    return redirect('/spotimatch')

@app.route('/spotimatch', methods=["GET", "POST"])
def spotimatch():
    print(spc.get_currently_playing())
    print(spc.get_top_artists())
    print(spc.get_top_tracks())
    return render_template('spotimatch.html')


if __name__ == '__main__':
    app.run(port=3000)

