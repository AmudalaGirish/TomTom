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
                    return redirect('success_page')
                except IntegrityError as e:
                    # Handle IntegrityError, for example, duplicate entries
                    messages.error(request, 'IntegrityError: {}'.format(str(e)))
            else:
                # Handle the case when coordinates are not available
                messages.error(request, 'Error getting coordinates. Please try again.')
    else:
        form = RideForm()

    return render(request, 'maps/ride_request.html', {'form': form})

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
