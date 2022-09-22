from dotenv import load_dotenv
from flask import Flask, request, jsonify, session, abort, redirect
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import os
import pathlib
import requests
import google.auth.transport.requests
from .objectid import PydanticObjectId
from .models import Trip, User

load_dotenv() # use dotenv to hide sensitive credential as environment variables
app = Flask(__name__)

app.secret_key = os.environ.get('APP_SECRET_KEY') # it is necessary to set a password when dealing with OAuth 2.0
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # this is to set our environment to https because OAuth 2.0 only supports https environments

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_AUTH_CLIENT_ID')  # enter your client id you got from Google console
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, 'client_secret.json')  # set the path to where the .json file you got Google console is

flow = Flow.from_client_secrets_file(  # Flow is OAuth 2.0 a class that stores all the information on how we want to authorize our users
    client_secrets_file=client_secrets_file,
    scopes=['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid'],  # here we are specifing what do we get after the authorization
    redirect_uri='https://127.0.0.1:5000/login/callback'  # and the redirect URI is the point where the user will end up after the authorization
)

MONGO_ATLAS_DATABASE_URL=f'mongodb+srv://{os.environ.get("MONGO_ATLAS_USERNAME")}:{os.environ.get("MONGO_ATLAS_PASSWORD")}'\
            f'@{os.environ.get("MONGO_ATLAS_CLUSTER")}.pusjb.mongodb.net/{os.environ.get("MONGO_ATLAS_DB_NAME")}?'\
            'retryWrites=true&w=majority' # get connection url from environment

app.config['MONGO_URI'] = os.environ.get("MONGO_DATABASE_URL") or MONGO_ATLAS_DATABASE_URL
client = PyMongo(app)
trips = client.db.trips
users = client.db.users

def authorize():
    if 'google_id' not in session:  # authorization required
        return abort(401)
    else:
        return True

@app.route('/login')  # the page where the user can login
def login():
    authorization_url, state = flow.authorization_url()  # asking the flow class for the authorization (login) url
    session['state'] = state
    return redirect(authorization_url)

@app.route('/login/callback') # this is the page that will handle the callback process meaning process after the authorization
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session['state'] == request.args['state']:
        abort(500) # state does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    user = {}
    session['google_id'] = user['google_id'] = id_info.get('sub')
    session['name'] = user['name'] = id_info.get('name')
    session['email'] = user['email'] = id_info.get('email')
    # session['profile_pic'] = user['profile_pic'] = id_info.get('picture')

    doc = users.update_one({ 'google_id': session['google_id'] }, { '$set': user }, upsert=True)

    # upserted_user = User(**user)
    # upserted_user.id = PydanticObjectId(str(doc.upserted_id)) if doc.upserted_id else None

    return 'Usuário autenticado com sucesso!'

@app.route('/logout')
def logout():
    session.clear()
    return 'Logout efetuado com sucesso!'

@app.errorhandler(404)
def resource_not_found(e):
    """
    An error-handler to ensure that 404 errors are returned as JSON.
    """
    return jsonify(error=str(e)), 404


@app.errorhandler(DuplicateKeyError)
def resource_not_found(e):
    """
    An error-handler to ensure that MongoDB duplicate key errors are returned as JSON.
    """
    return jsonify(error=f"Duplicate key error."), 400

@app.route('/')
def index():
    return '<h3> Ehptur v0.1.0 </h3>'

@app.route('/trips', methods=['GET'])
def read_trips():
    authorize()

    args = {}
    category_filter = request.args.getlist('categories') if len(request.args) and len(request.args['categories'])  else None
    string_search_filter = request.args.get('search') if len(request.args) else None

    if category_filter:
        args = {
            **args,
            'categories': { '$in': category_filter }
        }
    if string_search_filter:
        args = {
            **args,
            '$or': [
                { 'name': { '$regex': string_search_filter, '$options': 'i' } },
                { 'description': { '$regex': string_search_filter, '$options': 'i' } }
            ]
        }

    all_trips = trips.find(args)

    return { "trips": [Trip(**doc).to_json() for doc in all_trips], }

@app.route('/trips', methods=['POST'])
def create_trip():
    authorize()

    payload = request.get_json()

    trip = Trip(**payload)

    doc = trips.insert_one(trip.to_bson())

    trip.id = PydanticObjectId(str(doc.inserted_id))

    return trip.to_json()

@app.route('/users/<google_id>/city', methods=['PUT'])
def update_city_user(google_id):
    authorize()

    payload = request.get_json()

    # TODO - Validar cidade, só pode ser uma das cidades que tiver no banco (um select)
    if 'city' not in payload:
        abort(422) # city is required

    doc = users.update_one({ 'google_id': google_id }, { '$set': { 'city': payload['city'] } })
    if not doc.matched_count:
        abort(404)

    return 'Cidade do usuário configurada com sucesso'