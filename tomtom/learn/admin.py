from django.contrib import admin
from .models import *
# Register your models here.
admin.site.site_header = "Admin"

class EmpAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['eno', 'ename', 'esal']

admin.site.register(Emp, EmpAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Student)
