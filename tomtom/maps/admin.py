
from django.contrib import admin
from .models import Ride

class RideAdmin(admin.ModelAdmin):
    list_display = ('pickup_address', 'drop_address', 'pickup_latitude', 'pickup_longitude', 'drop_latitude', 'drop_longitude')

admin.site.register(Ride, RideAdmin)
