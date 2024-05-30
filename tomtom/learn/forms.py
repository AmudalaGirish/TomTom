from django.core import validators
from django import forms
from .models import *


def minlen(value):
    if len(value)<4:
        raise forms.ValidationError("Name must be greater than 4")

class StudentForm(forms.Form):
    name = forms.CharField(max_length=100, validators=[minlen])
    marks = forms.IntegerField(validators=[validators.MinValueValidator(40)])
    password = forms.CharField(widget=forms.PasswordInput)
    rpassword = forms.CharField(label="Re-enter Password", widget=forms.PasswordInput)
    bot_handler = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean(self):
        cleaned_data = super().clean()
        p = cleaned_data['password']
        rp = cleaned_data['rpassword']
        if p and rp and p!=rp:
            raise forms.ValidationError("Passwords do not match")
        
        if cleaned_data['bot_handler']:
            raise forms.ValidationError("Bot Detected")
        return cleaned_data
    




    # django form validation by using clean methods are not recomemnded

    # def clean_name(self):
    #     print("Validating name")
    #     name = self.cleaned_data['name']
    #     if len(name)<4:
    #         raise forms.ValidationError("Name must be greater than 4")
    #     return name

    # def clean_marks(self):
    #     marks = self.cleaned_data['marks']
    #     if marks<40:
    #         raise forms.ValidationError("Marks must be greater than 40")
        
    #     return marks

class StudentModelForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = "__all__"

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = "__all__"

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = "__all__"
        