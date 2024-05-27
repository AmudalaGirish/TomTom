from django.contrib import admin
from .models import *
# Register your models here.
admin.site.site_header = "Admin"

class EmpAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']

admin.site.register(Emp, EmpAdmin)
