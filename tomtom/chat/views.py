# chat/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def role_based_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.profile.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('emp_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'chat/login.html', {'form': form})

@login_required
def admin_dashboard(request):
    return render(request, 'chat/admin_dashboard.html')

@login_required
def emp_dashboard(request):
    return render(request, 'chat/emp_dashboard.html')

@login_required
def chat_page(request):
    users = User.objects.exclude(username=request.user.username)
    return render(request, 'chat/chat.html', {'users': users})