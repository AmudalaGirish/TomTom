from django.urls import path
from .views import ride_request, geocoding, reverse_geocoding

urlpatterns = [
    path('ride/request/', ride_request, name='ride_request'),
    path('geocoding/', geocoding, name='geocoding'),
    path('reverse_geocoding/', reverse_geocoding, name='reverse_geocoding'),
]
