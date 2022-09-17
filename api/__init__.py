from unicodedata import category
from dotenv import load_dotenv
from flask import Flask, request
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError
from bson import json_util
import json
import os

from .objectid import PydanticObjectId
from .models import Trip

load_dotenv() # use dotenv to hide sensitive credential as environment variables
app = Flask(__name__)

MONGO_ATLAS_DATABASE_URL=f'mongodb+srv://{os.environ.get("MONGO_ATLAS_USERNAME")}:{os.environ.get("MONGO_ATLAS_PASSWORD")}'\
            f'@{os.environ.get("MONGO_ATLAS_CLUSTER")}.pusjb.mongodb.net/{os.environ.get("MONGO_ATLAS_DB_NAME")}?'\
            'retryWrites=true&w=majority' # get connection url from environment

app.config['MONGO_URI'] = os.environ.get("MONGO_DATABASE_URL") or MONGO_ATLAS_DATABASE_URL
client = PyMongo(app)
trips = client.db.trips

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
    payload = request.get_json()

    trip = Trip(**payload)

    doc = trips.insert_one(trip.to_bson())

    trip.id = PydanticObjectId(str(doc.inserted_id))

    return trip.to_json()
