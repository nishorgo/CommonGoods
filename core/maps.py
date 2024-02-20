import googlemaps
from django.conf import settings
import requests
import json



def calculate_distance(origin, destination):
    gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
    response = gmaps.distance_matrix(origin, destination, mode='driving')
    distance = response['rows'][0]['elements'][0]['distance']['value'] / 1000
    return distance


def get_directions(locations):
    url = "https://maps.googleapis.com/maps/api/directions/json?"
    params = {
        "origin": f"{locations[0]['lat']},{locations[0]['lng']}",
        "destination": f"{locations[-1]['lat']},{locations[-1]['lng']}",
        "travelMode": 'DRIVING',
        "key": settings.GOOGLE_API_KEY
    }

    waypoints = []
    for location in locations[1:-1]:
        waypoints.append(f"{location['lat']},{location['lng']}")

    if waypoints:
        params['waypoints'] = 'optimize:true|' + '|'.join(waypoints) 

    response = requests.get(url, params=params)

    if response.status_code == 200:
        directions_data = json.loads(response.text)
        return directions_data
    else:
        return None


def reverse_geocode(coordinates):
    """
    Performs reverse geocoding and extracts a formatted address.
    coordinates: A tuple of (latitude, longitude)
    """
    gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
    results = gmaps.reverse_geocode(coordinates)
    if results:
        return results[0]['formatted_address']
    else:
        return None  #  In case no address is found