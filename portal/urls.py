from django.urls import path
from .views import *
urlpatterns = [
    path(route='',view=home_screen,name='home'),
    path(route='get_city_weather',view=get_city_weather_forecast,name='get_city_weather')
]
