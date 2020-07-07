from flask import Flask, request

import requests
import json

import googlemaps

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
gmaps = googlemaps.Client(API_KEY)

app = Flask(__name__)


PLACES_API_URL = 'http://localhost:8080/places'


def request_route_stats(headers, apartment_id, favorite_id):

    return response_data


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
        authenticated_headers = {"Authorization": auth_req_header}

        apartments_request_response = requests.get(
            f'{PLACES_API_URL}/apartments/{apartment_id}', headers=authenticated_headers)
        apartments_request_response.raise_for_status()

        favorites_request_response = requests.get(
            f'{PLACES_API_URL}/favorites/{favorite_id}', headers=authenticated_headers)
        favorites_request_response.raise_for_status()

        apt = apartments_request_response.json()
        fav = favorites_request_response.json()

        apt_address = f'{apt["street_address"]}, {apt["state"]} {apt["zip_code"]}'
        fav_address = f'{fav["street_address"]}, {fav["state"]} {fav["zip_code"]}'

        directions_data = gmaps.directions(
            apt_address, fav_address, mode="transit")

        leg = directions_data[0]["legs"][0]

        response_data = {
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
        print(error_name)

        if error_name == "HTTPError":
            status_code = int(str(err)[0:4])
            return "", status_code

        return "", 500

    return stats
