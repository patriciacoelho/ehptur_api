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
from bson.objectid import ObjectId
from datetime import datetime

from .objectid import PydanticObjectId
from .models import Trip, User, City, Operator, Itinerary, Tagged, Category

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
cities = client.db.cities
operators = client.db.operators
itineraries = client.db.itineraries
taggeds = client.db.taggeds
categories = client.db.categories

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
    # authorize()

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
    # authorize()

    payload = request.get_json()

    trip = Trip(**payload)

    doc = trips.insert_one(trip.to_bson())

    trip.id = PydanticObjectId(str(doc.inserted_id))

    return trip.to_json()

@app.route('/cities', methods=['GET'])
def read_cities():
    # authorize()

    all_cities = cities.find()

    return { "cities": [City(**doc).to_json() for doc in all_cities], }

@app.route('/users/<google_id>/city', methods=['PUT'])
def update_city_user(google_id):
    # authorize()

    payload = request.get_json()

    if 'city_id' not in payload:
        abort(422) # city is required
    city = cities.find_one({ '_id': ObjectId(payload['city_id']) })

    if not city:
        abort(422)

    doc = users.update_one({ 'google_id': google_id }, { '$set': { 'city_id': payload['city_id'] } })
    if not doc.matched_count:
        abort(404)

    return 'Cidade do usuário configurada com sucesso'

@app.route('/operators', methods=['GET'])
def read_operators():
    # authorize()

    args = { 'inactive': { '$ne': True } }
    string_search_filter = request.args.get('search') if len(request.args) else None
    pickup_id_filter = request.args.get('pickup_id') if len(request.args) else None
    pickup_filter = request.args.get('pickup') if len(request.args) else None
    # TODO - Filtro por destino "dropoff"

    if string_search_filter:
        args = {
            **args,
            'name': { '$regex': string_search_filter, '$options': 'i' },
        }

    city = None
    if pickup_id_filter:
        city = cities.find_one({ '_id': ObjectId(pickup_id_filter) })
    if not city and pickup_filter:
        city = cities.find_one({ 'name': { '$regex': pickup_filter, '$options': 'i' } })

    if city:
        city_id = str(city.get('_id'))
        args = {
            **args,
            'pickup_city_ids': { '$in': [city_id] },
        }

    all_operators = operators.find(args)

    return { 'operators': [Operator(**doc).to_json() for doc in all_operators], }

@app.route('/operators/<id>', methods=['GET'])
def read_operator(id):
    # authorize()

    doc = operators.find_one({ '_id': ObjectId(id) })

    return { 'operator': Operator(**doc).to_json(), }

@app.route('/itineraries/<id>', methods=['GET'])
def read_itinerary(id):
    # authorize()

    doc = itineraries.find_one({ '_id': ObjectId(id) })

    itinerary = Itinerary(**doc).to_json()

    itinerary['formatted_date'] = datetime.strftime(doc.get('date'), '%d/%m/%y')

    operator_id = doc.get('operator_id')
    operator = operators.find_one({ '_id': ObjectId(operator_id) })
    itinerary['operator'] = Operator(**operator).to_json()

    trip_id = doc.get('trip_id')
    trip = trips.find_one({ '_id': ObjectId(trip_id) })
    itinerary['trip'] = Trip(**trip).to_json()

    pickup_city_ids = doc.get('pickup_city_ids')
    pickup_cities = []
    for city_id in pickup_city_ids:
        city = cities.find_one({ '_id': ObjectId(city_id) })
        if (city):
            pickup_cities.append(City(**city).to_json())
    itinerary['pickup_cities'] = pickup_cities

    return { 'itinerary': itinerary, }

@app.route('/itineraries', methods=['GET'])
def read_itineraries():
    # authorize()

    args = {}

    take_filter = int(request.args.get('take')) if len(request.args) and request.args.get('take') else 0
    string_search_filter = request.args.get('search') if len(request.args) else None
    category_filter = request.args.getlist('categories') if len(request.args) else None
    if string_search_filter or category_filter:
        trip_ids_filter = []
        trips_query = {}
        if string_search_filter:
            trips_query = {
                '$or': [
                    { 'name': { '$regex': string_search_filter, '$options': 'i' } },
                    { 'description': { '$regex': string_search_filter, '$options': 'i' } },
                    { 'dropoff_location': { '$regex': string_search_filter, '$options': 'i' } }
                ]
            }
        if category_filter:
            trips_query = {
                **trips_query,
                'categories': { '$in': category_filter }
            }
        filtered_trips = trips.find(trips_query)
        trip_ids_filter = [str(trip.get('_id')) for trip in filtered_trips]

        args = {
            **args,
            'trip_id': { '$in': trip_ids_filter },
        }

    pickup_id_filter = request.args.get('pickup_id') if len(request.args) else None
    if pickup_id_filter:
        city = cities.find_one({ '_id': ObjectId(pickup_id_filter) })
        if city:
            city_id = str(city.get('_id'))
            args = {
                **args,
                'pickup_city_ids': { '$in': [city_id] },
            }

    operator_id_filter = request.args.get('operator_id') if len(request.args) else None
    if operator_id_filter:
        args = {
            **args,
            'operator_id': operator_id_filter,
        }

    classification_filter = request.args.get('classification') if len(request.args) else None
    if classification_filter:
        args = {
            **args,
            'classification': classification_filter,
        }

    min_price_filter = int(request.args.get('min_price')) if len(request.args) and request.args.get('min_price') else 0
    max_price_filter = int(request.args.get('max_price')) if len(request.args) and request.args.get('max_price') else 15000
    args = {
        **args,
        'price': { '$gte' : min_price_filter, '$lte' : max_price_filter},
    }

    start_date_filter = request.args.get('start_date') if len(request.args) and request.args.get('start_date') else '2022-01-01'
    end_date_filter = request.args.get('end_date') if len(request.args) and request.args.get('end_date') else '2092-01-01'
    args = {
        **args,
        'date': { '$gte' : datetime.fromisoformat(start_date_filter), '$lt' : datetime.fromisoformat(end_date_filter) },
    }

    docs = itineraries.find({ '$query': args, '$orderby': { 'date' : 1 } }).limit(take_filter)

    all_itineraries = []
    for doc in docs:
        itinerary = Itinerary(**doc).to_json()

        itinerary['formatted_date'] = datetime.strftime(doc.get('date'), '%d/%m/%y')

        operator_id = doc.get('operator_id')
        operator = operators.find_one({ '_id': ObjectId(operator_id) })
        itinerary['operator'] = Operator(**operator).to_json()

        trip_id = doc.get('trip_id')
        trip = trips.find_one({ '_id': ObjectId(trip_id) })
        itinerary['trip'] = Trip(**trip).to_json()

        pickup_city_ids = doc.get('pickup_city_ids')
        pickup_cities = []
        for city_id in pickup_city_ids:
            city = cities.find_one({ '_id': ObjectId(city_id) })
            if (city):
                pickup_cities.append(City(**city).to_json())
        itinerary['pickup_cities'] = pickup_cities
        all_itineraries.append(itinerary)

    return { 'itineraries': all_itineraries, }

@app.route('/taggeds/<user_id>', methods=['GET'])
def read_taggeds(user_id):
    # authorize()

    itinerary_id = request.args.get('itinerary_id') if len(request.args) else None
    trip_id = request.args.get('trip_id') if len(request.args) else None
    already_know = True if len(request.args) and request.args.get('already_know') == 'true' else False

    args = {
        'user_id': user_id,
        'already_know': already_know,
    }

    if itinerary_id:
        args = {
            **args,
            'itinerary_id': itinerary_id,
        }
    if trip_id:
        args = {
            **args,
            'trip_id': trip_id,
        }

    docs = taggeds.find(args)

    all_taggeds = []
    for doc in docs:
        tagged = Tagged(**doc).to_json()

        trip_id = doc.get('trip_id')
        itinerary_id = doc.get('itinerary_id')
        if (itinerary_id):
            found_itinerary = itineraries.find_one({ '_id': ObjectId(itinerary_id) })
            itinerary = Itinerary(**found_itinerary).to_json()

            tagged['classification'] = itinerary.get('classification')
            date = datetime.fromisoformat(itinerary.get('date'))
            tagged['formatted_date'] = datetime.strftime(date, '%d/%m/%y')

            operator_id = itinerary.get('operator_id')
            found_operator = operators.find_one({ '_id': ObjectId(operator_id) })
            operator = Operator(**found_operator).to_json()
            tagged['operator_name'] = operator.get('name')

            trip_id = itinerary.get('trip_id')

        found_trip = trips.find_one({ '_id': ObjectId(trip_id) })
        trip = Trip(**found_trip).to_json()
        tagged['trip_name'] = trip.get('name')
        tagged['image_url'] = trip.get('image_url')

        all_taggeds.append(tagged)

    return { 'taggeds': all_taggeds, }

@app.route('/taggeds', methods=['POST'])
def create_tagged():
    # authorize()

    payload = request.get_json()

    tagged = Tagged(**payload)

    doc = taggeds.insert_one(tagged.to_bson())

    tagged.id = PydanticObjectId(str(doc.inserted_id))

    return tagged.to_json()

@app.route('/categories', methods=['GET'])
def read_categories():
    # authorize()

    all_categories = categories.find()

    return { "categories": [Category(**doc).to_json() for doc in all_categories], }