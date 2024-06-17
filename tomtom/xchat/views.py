from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def main_view(request):
    context = {}
    return render(request, 'xchat/main.html', context=context)

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
                    return redirect('admin')
                else:
                    return redirect('emp')
    else:
        form = AuthenticationForm()
    return render(request, 'xchat/login.html', {'form': form})

@login_required
def admin_dashboard(request):
    return render(request, 'xchat/admin_dashboard.html')

@login_required
def emp_dashboard(request):
    return render(request, 'xchat/emp_dashboard.html')
