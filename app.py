from flask import Flask, request, jsonify
from flask_cors import CORS

import requests
import json

import googlemaps

import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("API_KEY")
PLACES_API_URL = 'http://localhost:8080/places'

app = Flask(__name__)
CORS(app)


gmaps = googlemaps.Client(GOOGLE_API_KEY)


def query_google_directions_api(apartment_id, favorite_id, headers={}):
    apartments_request_response = requests.get(
        f'{PLACES_API_URL}/apartments/{apartment_id}', headers=headers)
    apartments_request_response.raise_for_status()

    favorites_request_response = requests.get(
        f'{PLACES_API_URL}/favorites/{favorite_id}', headers=headers)
    favorites_request_response.raise_for_status()

    apt = apartments_request_response.json()
    fav = favorites_request_response.json()

    apt_address = f'{apt["street_address"]}, {apt["state"]} {apt["zip_code"]}'
    fav_address = f'{fav["street_address"]}, {fav["state"]} {fav["zip_code"]}'

    directions_request_data = gmaps.directions(
        apt_address, fav_address, mode="transit")

    directions_data = directions_request_data[0]

    directions_data["apartment"] = apt
    directions_data["favorite"] = fav

    return directions_data


@app.route('/commutes/stats')
def get_commute_stats():

    auth_req_header = request.headers.get('Authorization')

    apartment_id = request.args.get('apartment_id')
    favorite_id = request.args.get('favorite_id')

    if auth_req_header == None:
        return "Unauthorized", 401

    if apartment_id == None or favorite_id == None:
        return "Missing Parameters", 403

    try:
        authenticated_header = {"Authorization": auth_req_header}
        directions_data = query_google_directions_api(
            apartment_id, favorite_id, authenticated_header)

        leg = directions_data["legs"][0]
        apt = directions_data["apartment"]
        fav = directions_data["favorite"]

        stats = {
            "from": {
                "place_type": "APARTMENT",
                "_id": apt["_id"]["$oid"],
                "address": leg["start_address"],
                "coords": leg["start_location"],
            },
            "to": {
                "place_type": "FAVORITE",
                "_id": fav["_id"]["$oid"],
                "address": leg["end_address"],
                "coords": leg["end_location"],
            },
            "distance": leg["distance"],
            "duration": leg["duration"]
        }

    except Exception as err:
        error_name = type(err).__name__
        if error_name == "HTTPError":
            status_code = int(str(err)[0:4])
            return "", status_code
        print(err)
        return "", 500

    return stats


@app.route('/commutes')
def get_commute():
    auth_req_header = request.headers.get('Authorization')

    apartment_id = request.args.get('apartment_id')
    favorite_id = request.args.get('favorite_id')

    if auth_req_header == None:
        return "Unauthorized", 401

    if apartment_id == None or favorite_id == None:
        return "Missing Parameters", 403

    try:
        authenticated_header = {"Authorization": auth_req_header}
        directions_data = query_google_directions_api(
            apartment_id, favorite_id, authenticated_header)

        commute = jsonify(directions_data)

        return commute

    except Exception as err:
        error_name = type(err).__name__
        if error_name == "HTTPError":
            status_code = int(str(err)[0:4])
            return "", status_code
        print(err)
        return "", 500
