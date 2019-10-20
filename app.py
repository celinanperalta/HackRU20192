from flask import *
from flask_oauthlib.client import OAuth, OAuthException
from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField
from config import *
from SpotifyController import SpotifyController

app = Flask(__name__)

SPOTIFY_APP_ID = client_id
SPOTIFY_APP_SECRET = client_secret

spc = SpotifyController()

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

spotify = oauth.remote_app(
    'spotify',
    consumer_key=SPOTIFY_APP_ID,
    consumer_secret=SPOTIFY_APP_SECRET,
    # Change the scope to match whatever it us you need
    # list of scopes can be found in the url below
    # https://developer.spotify.com/web-api/using-scopes/
    request_token_params={'scope': 'user-top-read user-read-email'},
    base_url='https://accounts.spotify.com',
    request_token_url=None,
    access_token_url='/api/token',
    authorize_url='https://accounts.spotify.com/authorize'
)

FEATURES = [(x,x) for x in ['danceability', 'loudness', 'speechiness', 'acousticness','instrumentalness', 'energy','tempo']]

class PlaylistForm(FlaskForm):
    username = StringField('username')
    features = SelectMultipleField("Features", choices=FEATURES)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login')
def login():
    callback = redirect_uri
    return spotify.authorize(callback=callback)

@app.route('/callback')
def spotify_authorized():
    resp = spotify.authorized_response()
    if resp is None:
        return 'Access denied: reason={0} error={1}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: {0}'.format(resp.message)

    session['oauth_token'] = (resp['access_token'], '')
    spc.authenticate_token(resp['access_token'])
    return redirect('/spotimatch')

@app.route('/spotimatch')
def spotimatch():
    # print(spc.get_currently_playing())
    # print(spc.get_top_artists())
    form = PlaylistForm()
    return render_template('spotimatch.html', profile=spc.user_profile, form=form)

@app.route('/update_playlists', methods=['POST'])
def update_playlists():
    form = PlaylistForm()

    if form.validate_on_submit():
        playlists = spc.get_api().user_playlists(form.username.data, 10, 0)
        playlist_names = [x['name'] for x in playlists['items']]
        playlist_ids = [x['id'] for x in playlists['items']]
        data = [spc.get_playlist_features(x) for x in playlist_ids]

        return str(data)

    #todo: split page into two parts to render separately
    return jsonify(data=form.errors)


@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')


if __name__ == '__main__':
    app.run(port=3000)

