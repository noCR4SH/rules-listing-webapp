"""Python Flask WebApp Auth0 integration example
"""
from functools import wraps
import json
import csv
from os import environ as env
from io import StringIO
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode

import reports
import constants

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)
AUTH0_M2M_AUDIENCE = env.get(constants.AUTH0_M2M_AUDIENCE)

app = Flask(__name__, static_url_path='/public', static_folder='./public')
app.secret_key = constants.SECRET_KEY
app.debug = True


@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


# Controllers API
@app.route('/')
def home():
    return render_template('login_page.html')


@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    session[constants.JWT_PAYLOAD] = userinfo
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/home')


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

@app.route('/report')
def report():
    pass

@app.route('/download_csv')
@requires_auth
def download_csv():
    bearer_token = reports.get_token(AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_M2M_AUDIENCE, AUTH0_DOMAIN)
    fetched_rules = reports.get_rules(bearer_token, AUTH0_M2M_AUDIENCE)
    final_data = reports.find_client(fetched_rules)

    def generate_csv():
        data = StringIO()
        w = csv.writer(data)

        w.writerow(('id', 'enabled', 'name', 'order', 'stage', 'client_name'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        for item in final_data:
            w.writerow((item['id'], item['enabled'], item['name'], item['order'], item['stage'], item['client_name']))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    response = Response(generate_csv(), mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename="report.csv")

    return response

@app.route('/home')
@requires_auth
def homepage():
    return render_template('index.html',
                           userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=env.get('PORT', 3000))
