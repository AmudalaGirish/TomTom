from django.shortcuts import render, redirect
import datetime
from django.http import HttpResponse
from .models import *


# Create your views here.
def appinfo(request):
    emp_list = Emp.objects.all()
    
    return render(request, 'index.html', context={'emps':emp_list})

def htttp(request):
    return HttpResponse("<h1> Hello World</h1>")

from .forms import *
from django.contrib.auth.decorators import login_required

def studentinputview(request):
    form = StudentForm()
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
    return render(request, 'studentinput.html', {'form':form})

def studentmodelform(request):
    form = StudentModelForm()
    if request.method == 'POST':
        form = StudentModelForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
    return render(request, 'studentinput.html', {'form':form})


# cookies views
def testcookie(request):
    if 'count' in request.COOKIES:
        count = int(request.COOKIES['count']) + 1
    else:
        count = 1
    response = HttpResponse(f"<h1>This page has been visited {count} times</h1>")
    response.set_cookie('count', count)
    return response
def checkcookie(request):
    name = request.COOKIES.get('name')
    return HttpResponse(name)


def itemhome(request):
    return render(request, 'itemhome.html')

def additem(request):
    form = ItemForm()
    response = render(request, 'additem.html', {'form':form})
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            quantity = form.cleaned_data['quantity']
            response.set_cookie(name, quantity, max_age=60*60*24)
    return response

def displayitem(request):
    items = {}
    for key in request.COOKIES:
        items[key] = request.COOKIES[key]
    return render(request, 'displayitem.html', {'items':items})

# Seesion Views
@login_required
def seesion_count(request):
    count = request.session.get('count', 0)
    request.session['name'] = 'Raj'
    newcount = count + 1
    request.session['count'] = newcount
    print(request.session.get_expiry_age())
    print(request.session.get_expiry_date())
    return HttpResponse(f"<h1>This page has been visited {newcount} times</h1>")

def session_check(request):
    count = request.session.get('count', 0)
    name = request.session.get('name', 'Guest')
    return HttpResponse(f"<h1>geting session count {count} times & {name}</h1>")



# Function based views example views

def list_view(request):
    employees = Employee.objects.all()
    return render(request, 'showemp.html', {'emps':employees})

def create_view(request):
    form = EmployeeForm()
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('list')
    return render(request, 'createemp.html', {'form':form})

def update_view(request, id):
    emp = Employee.objects.get(id=id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=emp)
        if form.is_valid():
            form.save()
        return redirect('list')
    return render(request, 'createemp.html', {'emp':emp})

def delete_view(request, id):
    emp = Employee.objects.get(id=id)
    emp.delete()
    return redirect('list')
