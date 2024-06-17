from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', main_view),
    path('login/', role_based_login, name='login'),
    path('admin_dashboard/', admin_dashboard, name='admin'),
    path('emp_dashboard/', emp_dashboard, name='emp'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]