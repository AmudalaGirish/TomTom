from django.urls import path
from .views import ride_request,success_page, geocoding, reverse_geocoding

urlpatterns = [
    path('ride/request/', ride_request, name='ride_request'),
    path('success-page/<str:pickup_lon>/<str:pickup_lat>/<str:drop_lon>/<str:drop_lat>/', success_page, name='success_page'),
    path('geocoding/', geocoding, name='geocoding'),
    path('reverse_geocoding/', reverse_geocoding, name='reverse_geocoding'),
]
