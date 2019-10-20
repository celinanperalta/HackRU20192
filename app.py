from flask import *
from flask_oauthlib.client import OAuth, OAuthException
from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from config import *
from SpotifyController import SpotifyController
import json

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

USER_FEATURES = ['danceability', 'loudness', 'speechiness', 'acousticness','instrumentalness', 'energy','tempo']
FEATURES = [(x,x) for x in ['danceability', 'loudness', 'speechiness', 'acousticness','instrumentalness', 'energy','tempo']]
RANGES = {
    'danceability' : 1,
    'loudness' : 60,
    'speechiness' : 1,
    'acousticness' : 1,
    'instrumentalness' : 1,
    'energy' : 1,
    'tempo' : 225
}


class MultiCheckboxField(SelectMultipleField):
    widget          = ListWidget(prefix_label=False)
    option_widget   = CheckboxInput()

class PlaylistForm(FlaskForm):
    username = StringField('username')
    features = MultiCheckboxField("Features", choices=FEATURES)

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
    return render_template('spotimatch.html', profile=spc.user_profile, form=form, user_features=json.dumps(USER_FEATURES), avg_features=json.dumps(list(spc.avg_features.values())))

@app.route('/update_playlists', methods=['POST'])
def update_playlists():
    form = PlaylistForm()

    if form.validate_on_submit():

        playlists = spc.get_api().user_playlists(form.username.data, 10, 0)
        filters = form.features.data
        playlist_names = [x['name'] for x in playlists['items']]
        playlist_ids = [x['id'] for x in playlists['items']]
        playlist_urls = [x['external_urls']['spotify'] for x in playlists['items']]
        playlist_features = [spc.get_playlist_features(x, filters) for x in playlist_ids]

        scores = {}
        urls = {}

        for i in range(0, len(playlist_features)):
            scores[playlist_names[i]] = score(spc.avg_features, playlist_features[i], filters)
            urls[playlist_names[i]] = playlist_urls[i]

        scores = dict(sorted(scores.items(), key = lambda kv:(kv[1], kv[0]), reverse=True))
        score_keys = list(scores.keys())

        print(scores)

        html = '<table><thead><th>Playlist</th><th>Score</th></thead>'


        for i in range(0, len(scores)):
            html += '<tr><td><a href="' + urls[score_keys[i]] + '">' + score_keys[i] + '</a></td><td>' + str(scores[score_keys[i]]) + '</td></tr>'

        html += '</table>'

        return html

    #todo: split page into two parts to render separately
    return jsonify(data=form.errors)


def score(avg_features, playlist_features, filters):
    s = 0
    for filter in filters:
        s += (1-(abs(avg_features[filter]-playlist_features[filter]))/RANGES[filter])*100/len(filters)
    return s

@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')


if __name__ == '__main__':
    app.run(port=3000)

