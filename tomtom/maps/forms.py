from django import forms
from .models import Ride, Employee, Client


class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['pickup_address', 'pickup_address_1',
                  'pickup_address_2', 'drop_address']

    def __init__(self, *args, **kwargs):
        super(RideForm, self).__init__(*args, **kwargs)
        self.fields['pickup_address'].label = 'Main Pickup Address'
        self.fields['pickup_address_1'] = forms.CharField(
            label='Pickup Address 1', required=False)
        self.fields['pickup_address_2'] = forms.CharField(
            label='Pickup Address 2', required=False)

    def clean(self):
        cleaned_data = super().clean()
        pickup_address = cleaned_data.get('pickup_address')
        pickup_address_1 = cleaned_data.get('pickup_address_1')
        pickup_address_2 = cleaned_data.get('pickup_address_2')

        if not pickup_address and not pickup_address_1 and not pickup_address_2:
            raise forms.ValidationError(
                'At least one pickup address is required.')

        return cleaned_data


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['emp_id', 'name', 'address']


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'address']
