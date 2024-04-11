from django.contrib import admin
from .models import Ride, Employee, Client, Payment
from .forms import EmployeeForm, ClientForm


class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'pickup_address', 'pickup_address_1', 'pickup_address_2', 'drop_address', 'pickup_latitude', 'pickup_longitude',
                    'pickup_latitude_1', 'pickup_longitude_1', 'pickup_latitude_2', 'pickup_longitude_2', 'drop_latitude', 'drop_longitude')


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('emp_id', 'name', 'address', 'latitude', 'longitude')
    form = EmployeeForm


class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'latitude', 'longitude')
    form = ClientForm


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'order_id',
                    'razorpay_payment_id', 'paid')


admin.site.register(Ride, RideAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Payment, PaymentAdmin)
