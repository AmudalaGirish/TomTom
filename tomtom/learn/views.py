from django.shortcuts import render
import datetime
from django.http import HttpResponse
from .models import *

# Create your views here.
def appinfo(request):
    emp_list = Emp.objects.all()
    
    return render(request, 'index.html', context={'emps':emp_list})