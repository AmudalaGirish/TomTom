from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import RideForm
from .utils import get_coordinates
from django.db import IntegrityError
from django.contrib import messages
from django.conf import settings
from .models import Employee, Client
from .forms import EmployeeForm, ClientForm
from django.views.decorators.http import require_GET
from django.db.models import F, Func, FloatField

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
    # api_key = settings.TOM_API_KEY

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
        # api_key = settings.TOM_API_KEY

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
    
def emp_list(request):
    employees = Employee.objects.all()
    return render(request, 'maps/emp_list.html', {'employees':employees})

def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_list')

    else:
        form = EmployeeForm()

    return render(request, 'maps/add_emp.html', {'form':form})

def client_list(request):
    clients = Client.objects.all()
    return render(request, 'maps/client_list.html', {'clients':clients})

def add_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_list')

    else:
        form = EmployeeForm()

    return render(request, 'maps/add_client.html', {'form':form})

def get_clients(request):
    clients = Client.objects.all()
    client_data = [{'id': client.id, 'name': client.name} for client in clients]
    return JsonResponse({'clients': client_data})

def get_employees(request):
    employees = Employee.objects.all()
    employee_data = [{'id': employee.id, 'name': employee.name} for employee in employees]
    return JsonResponse({'employees': employee_data})

def get_client_details(request, pk):
    if request.method == 'GET':
        try:
            client = get_object_or_404(Client, pk=pk)
            client_details = {
                'id': client.id,
                'address': client.address,
                'latitude': float(client.latitude) if client.latitude is not None else None,
                'longitude': float(client.longitude) if client.longitude is not None else None,
            }
            return JsonResponse(client_details)
        except Client.DoesNotExist:
            return JsonResponse({'error': 'Client not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
def get_employee_details(request, pk):
    if request.method == 'GET':
        try:
            employee = get_object_or_404(Employee, pk=pk)
            employee_details = {
                'id': employee.id,
                'emp_id': employee.emp_id,
                'name': employee.name,
                'address': employee.address,
                'longitude': float(employee.longitude) if employee.longitude is not None else None,
                'latitude': float(employee.latitude) if employee.latitude is not None else None,
            }

            return JsonResponse(employee_details)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Employee not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

class DistanceExpression(Func):
    function = 'SQRT'
    arity = 1

    def __init__(self, expression, **extra):
        super().__init__(expression, **extra)
        self.output_field = FloatField()

@require_GET
def get_nearby_employees(request):
    # Assuming you have a Ride model with pickup and drop coordinates
    # Fetch the pickup and drop coordinates from the database
    pickup_coords = [request.GET.get('pickup_lon'), request.GET.get('pickup_lat')]
    drop_coords = [request.GET.get('drop_lon'), request.GET.get('drop_lat')]

    # Check if coordinates are valid
    if None in pickup_coords or None in drop_coords:
        return JsonResponse({'error': 'Invalid coordinates'})

    # Get nearby employees based on the pickup and drop coordinates
    # nearby_employees = Employee.objects.annotate(
    #     distance = F('latitude') + F('longitude') - (float(pickup_coords[0]) + float(pickup_coords[1]) + float(drop_coords[0]) + float(drop_coords[1]))
    # ).order_by('distance')[:5]  # Adjust the number of employees as needed

    # Get nearby employees based on the pickup and drop coordinates
    nearby_employees = Employee.objects.annotate(
        distance=DistanceExpression(
            (F('latitude') - pickup_coords[0]) ** 2 + (F('longitude') - pickup_coords[1]) ** 2
        )
    ).order_by('distance')[:5]
    # Add print statements to debug the values of each employee
    for employee in nearby_employees:
        print(f"Employee Name: {employee.name}, Latitude: {employee.latitude}, Longitude: {employee.longitude}")


    # Create a list of dictionaries containing employee details
    nearby_employees_list = [
        {
            'name': employee.name,
            'latitude': employee.latitude,
            'longitude': employee.longitude,
        }
        for employee in nearby_employees
    ]

    return JsonResponse({'nearby_employees': nearby_employees_list})