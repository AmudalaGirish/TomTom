from django.urls import path
from .views import *

urlpatterns = [
    path('ride/request/', ride_request, name='ride_request'),
    # path('success-page/<str:pickup_lon>/<str:pickup_lat>/<str:drop_lon>/<str:drop_lat>/', success_page, name='success_page'),
    path('success-page/<str:pickup_lon>/<str:pickup_lat>/<str:pickup_lon_1>/<str:pickup_lat_1>/<str:pickup_lon_2>/<str:pickup_lat_2>/<str:drop_lon>/<str:drop_lat>/',
         success_page, name='success_page'),
    path('search_location/', search_location,
         name='search_location'),  # Add this line
    path('employees/', emp_list, name='employee_list'),
    path('add_employee/', add_employee, name='add_employee'),
    path('clients/', client_list, name='client_list'),
    path('add_client/', add_client, name='add_client'),
    path('get_clients/', get_clients, name='get_clients'),
    path('get_employees/', get_employees, name='get_employees'),
    path('get_client_details/<int:pk>/',
         get_client_details, name='get_client_details'),
    path('get_employee_details/<int:pk>/',
         get_employee_details, name='get_employee_details'),
    path('get_nearby_employees/', get_nearby_employees,
         name='get_nearby_employees'),
    path('payment_form/', payment_form, name='payment_form'),
    path('payment_status/', payment_status, name='payment_status'),
    path('goto/', goto, name='goto'),
    path('payment_link/', generate_payment_link, name='payment_link'),
    path('payment_verify_link/', verify_payment_link_signature, name='payment_verify_link'),
    path('create_invoice/', create_invoice, name='create_invoice'),
    path('generate_invoice/', generate_invoice, name='generate_invoice'),
    path('generate-pdf/', generate_pdf, name='generate_pdf'),
]
