# maps/utils.py

import requests

def get_coordinates(address):
    """
    Get coordinates (latitude, longitude) for a given address using TomTom Geocoding API.
    """
    api_key = 'XMnfj9I0Mi7gwOGlLf6MMjGGBTvzIIh6'  # Replace with your TomTom API key
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
            return coordinates.get('latitude'), coordinates.get('longitude')
        else:
            print(f"Error getting coordinates for {address}: 'position' key not found in the response.")
            return None
    else:
        # Handle errors or return a default value
        print(f"Error getting coordinates for {address}: {data.get('message')}")
        return None
