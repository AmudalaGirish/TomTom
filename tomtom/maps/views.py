from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import RideForm
from .utils import get_coordinates
from django.db import IntegrityError
from django.contrib import messages

def ride_request(request):
    if request.method == 'POST':
        form = RideForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)

            # Get coordinates for pickup and drop addresses
            pickup_coords = get_coordinates(ride.pickup_address)
            drop_coords = get_coordinates(ride.drop_address)

            # Check if coordinates are available
            if pickup_coords and drop_coords:
                # Set the coordinates in the Ride object
                ride.pickup_latitude, ride.pickup_longitude = pickup_coords
                ride.drop_latitude, ride.drop_longitude = drop_coords

                try:
                    # Save the Ride object
                    ride.save()

                    # Redirect to a success page or handle as needed
                    return redirect('success_page', pickup_lon=ride.pickup_longitude, pickup_lat=ride.pickup_latitude, drop_lon=ride.drop_longitude, drop_lat=ride.drop_latitude)
                except IntegrityError as e:
                    # Handle IntegrityError, for example, duplicate entries
                    messages.error(request, 'IntegrityError: {}'.format(str(e)))
            else:
                # Handle the case when coordinates are not available
                messages.error(request, 'Error getting coordinates. Please try again.')
    else:
        form = RideForm()

    return render(request, 'maps/ride_request.html', {'form': form})

def success_page(request, pickup_lon, pickup_lat, drop_lon, drop_lat):
    # Convert parameters to float
    pickup_lon = float(pickup_lon)
    pickup_lat = float(pickup_lat)
    drop_lon = float(drop_lon)
    drop_lat = float(drop_lat)

    # Call a function to get the route data
    route_data = get_route_data(pickup_lon, pickup_lat, drop_lon, drop_lat)

    return render(request, 'maps/success_page.html', {
        'pickup_lon': pickup_lon,
        'pickup_lat': pickup_lat,
        'drop_lon': drop_lon,
        'drop_lat': drop_lat,
        'route_data': route_data,
    })
import requests

def get_route_data(pickup_lon, pickup_lat, drop_lon, drop_lat):
    # Replace 'YOUR_API_KEY' with your actual TomTom API key
    api_key = 'XMnfj9I0Mi7gwOGlLf6MMjGGBTvzIIh6'

    # TomTom Routing API endpoint
    routing_api_url = 'https://api.tomtom.com/routing/1/calculateRoute/{},{}:{},{}/json'.format(
        pickup_lat, pickup_lon, drop_lat, drop_lon
    )

    # Parameters for the API request
    params = {
        'key': api_key,
        'computeBestOrder': 'true',  # Optional: Calculate the best order for the waypoints
        'maxAlternatives': 0,       # Optional: Number of alternative routes
    }

    # Make the API request
    response = requests.get(routing_api_url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Check if 'routes' is present in the response
        if 'routes' in data and data['routes']:
            route = data['routes'][0]

            # Check if 'legs' is present in the route
            if 'legs' in route and route['legs']:
                leg = route['legs'][0]

                # Check if 'points' is present in the leg
                if 'points' in leg and leg['points']:
                    # Extract latitude and longitude from each point in the 'points' array
                    route_geometry = [[point['longitude'], point['latitude']] for point in leg['points']]
                else:
                    route_geometry = None
            else:
                # Handle the case when 'legs' is not found in the 'routes' section
                route_geometry = None
        else:
            # Handle the case when 'routes' is not found in the data
            route_geometry = None

        # Convert the data to GeoJSON format
        geojson_data = {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "LineString",
                "coordinates": route_geometry
            }
        }

        return {
            'pickup_coords': [pickup_lon, pickup_lat],
            'drop_coords': [drop_lon, drop_lat],
            'route_geometry': geojson_data,
        }
    else:
        # Handle API request failure
        print(response.status_code)
        print(response.text)
        return None

def search_location(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        api_key = 'XMnfj9I0Mi7gwOGlLf6MMjGGBTvzIIh6'

        # search API (TomTom)
        search_api_url = f'https://api.tomtom.com/search/2/search/{query}.json'

        params = {
            'key': api_key,
            'language': 'en-US',
        }

        response = requests.get(search_api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            locations = [{
                'name': result.get('address', {}).get('freeformAddress', ''),
                'latitude': result.get('position', {}).get('lat', ''),
                'longitude': result.get('position', {}).get('lon', ''),
            } for result in data.get('results', [])]

            return JsonResponse({'locations':locations})

        return JsonResponse({'error': 'Failed to fetch results'}, status=500)
    


def geocoding(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        # Implement your geocoding logic here using TomTom API
        # Use tt.services.geocoding(...) and return the results in a dictionary
        results = {
            # Include latitude, longitude, and other relevant information
            'latitude': -33.9249,
            'longitude': 18.4241,
            'address': 'Sample Address',
        }
        return JsonResponse(results)
    else:
        return render(request, 'maps/geocoding.html')

def reverse_geocoding(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        # Implement your reverse geocoding logic here using TomTom API
        # Use tt.services.reverseGeocoding(...) and return the results in a dictionary
        results = {
            # Include address components and other relevant information
            'address': 'Sample Address',
        }
        return JsonResponse(results)
    else:
        return render(request, 'maps/reverse_geocoding.html')
