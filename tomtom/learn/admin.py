from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
# Register your models here.
admin.site.site_header = "Admin"

class EmpAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['eno', 'ename', 'esal']

admin.site.register(Emp, EmpAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Student)
admin.site.register(BasicModel)
admin.site.register(StrandardModel)
