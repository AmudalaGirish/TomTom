from django import forms
from .models import Ride, Employee, Client

class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['pickup_address', 'drop_address']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['emp_id', 'name', 'address']

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'address']