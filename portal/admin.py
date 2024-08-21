from django.contrib import admin

# Register your models here.
from .models import SiteConfigs,WeatherData, Forecast, RadarData

admin.site.register(SiteConfigs)
admin.site.register(WeatherData)
admin.site.register(Forecast)
admin.site.register(RadarData)
