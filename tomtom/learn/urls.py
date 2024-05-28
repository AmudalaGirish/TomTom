from django.urls import path
from .views import *

urlpatterns = [
    path('test/', appinfo, name='appinfo'),
    path('stu/', studentinputview),
    path('student/', studentmodelform),
    path('testcookie/', testcookie),
    path('checkcookie/', checkcookie),

]