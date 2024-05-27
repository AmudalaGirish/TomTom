from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('chat/', views.chat_page, name='chat'),
    path('login/', views.role_based_login, name='login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('emp_dashboard/', views.emp_dashboard, name='emp_dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
