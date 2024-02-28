from django.urls import path
from .views import *

urlpatterns = [
    path('ride/request/', ride_request, name='ride_request'),
    path('success-page/<str:pickup_lon>/<str:pickup_lat>/<str:drop_lon>/<str:drop_lat>/', success_page, name='success_page'),
    path('search_location/', search_location, name='search_location'),  # Add this line
    path('employees/', emp_list, name='employee_list'),
    path('add_employee/', add_employee, name='add_employee'),
    path('clients/', client_list, name='client_list'),    
    path('add_client/', add_client, name='add_client'),
    path('get_clients/', get_clients, name='get_clients'),
    path('get_employees/', get_employees, name='get_employees'),
]
