from django.urls import path
from .views import *

urlpatterns = [
    path('test/', appinfo, name='appinfo'),
    
]