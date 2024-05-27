from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('maps/', include('maps.urls')),
    path('webpush/', include('webpush.urls')),
    path("chat/", include("chat.urls")),
    path('paypal/', include('paypal.urls')),
    path('learn/', include('learn.urls')),

]
