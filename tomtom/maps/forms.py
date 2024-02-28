from django import forms
from .models import Ride, Employee

class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['pickup_address', 'drop_address']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['emp_id', 'name', 'address']

