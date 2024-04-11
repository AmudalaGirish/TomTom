import requests
from django.conf import settings
from math import radians, sin, cos, sqrt, atan2
from django.db.models import F, Func, FloatField
from math import radians, sin, cos, sqrt, atan2

# Function to calculate Haversine distance between two points


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * \
        cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


def get_coordinates(address):
    """
    Get coordinates (latitude, longitude) for a given address using TomTom Geocoding API.
    """
    api_key = 'XMnfj9I0Mi7gwOGlLf6MMjGGBTvzIIh6'
    # api_key = settings.TOM_API_KEY  # Replace with your TomTom API key
    base_url = 'https://api.tomtom.com/search/2/geocode/{address}.json'

    # Prepare the URL with the address and API key
    url = base_url.format(address=address)
    params = {'key': api_key}

    # Make the request to TomTom Geocoding API
    response = requests.get(url, params=params)
    data = response.json()

    # Check if the request was successful
    if response.status_code == 200 and data.get('results'):
        # Extract coordinates from the response
        result = data['results'][0]
        if 'position' in result:
            coordinates = result['position']
            return coordinates.get('lat'), coordinates.get('lon')
        else:
            print(
                f"Error getting coordinates for {address}: 'position' key not found in the response.")
            return None
    else:
        # Handle errors or return a default value
        print(
            f"Error getting coordinates for {address}: {data.get('message')}")
        return None
