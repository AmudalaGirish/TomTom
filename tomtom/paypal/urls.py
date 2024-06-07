from django.urls import path
from .views import checkout_view, create_order, capture_order, CaptureOrderView, CreateOrderView

urlpatterns = [
    path('', checkout_view, name='checkout'),
    path('orders/', CreateOrderView.as_view(), name='create_order'),
    path('orders/<str:order_id>/capture', CaptureOrderView.as_view, name='capture_order'),
]
