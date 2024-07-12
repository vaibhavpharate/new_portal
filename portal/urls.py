from django.urls import path
from .views import *
urlpatterns = [
    path(route='',view=home_screen,name='home'),
]
