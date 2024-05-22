from django.urls import path
from .views import checkout_view, create_order, capture_order

urlpatterns = [
    path('', checkout_view, name='checkout'),
    path('orders/', create_order, name='create_order'),
    path('orders/<str:order_id>/capture', capture_order, name='capture_order'),
]
