from django.contrib import admin
from .models import Ride, Employee, Client
from .forms import EmployeeForm, ClientForm

class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'pickup_address', 'drop_address', 'pickup_latitude', 'pickup_longitude', 'drop_latitude', 'drop_longitude')

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('emp_id', 'name', 'address', 'latitude', 'longitude')
    form = EmployeeForm

class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude')
    form = ClientForm

admin.site.register(Ride, RideAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Client, ClientAdmin)
