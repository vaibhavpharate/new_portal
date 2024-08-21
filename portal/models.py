from django.db import models

# Create your models here.

class SiteConfigs(models.Model):
    cityname = models.CharField(max_length=50, blank=True, null=True)
    localityname = models.CharField(max_length=50, blank=True, null=True)
    localityid = models.CharField(db_column='localityId',max_length=50,unique=True,primary_key=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"zomato_sites". "site_configs"'

class WeatherData(models.Model):
    temperature = models.TextField(blank=True, null=True)
    humidity = models.TextField(blank=True, null=True)
    wind_speed = models.TextField(blank=True, null=True)
    wind_direction = models.TextField(blank=True, null=True)
    rain_intensity = models.TextField(blank=True, null=True)
    rain_accumulation = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    location_id = models.ForeignKey(SiteConfigs,on_delete=models.CASCADE,db_column='location_id')
    rain_index = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        managed = False
        db_table = '"zomato_new_actual"."weather_data"'


class Forecast(models.Model):
    localityid = models.ForeignKey(SiteConfigs,db_column='localityId',on_delete=models.CASCADE)  # Field name made lowercase.
    rain_intensity = models.FloatField(blank=True, null=True)
    rain_index = models.BigIntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    cityname = models.TextField(blank=True, null=True)
    localityname = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    device_type = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        managed = False
        db_table = '"zomato_forecast_kf"."forecast"'



class RadarData(models.Model):
    dbz_value = models.FloatField(blank=True, null=True)
    localityid = models.ForeignKey(SiteConfigs,db_column='localityId',on_delete=models.CASCADE)  # Field name made lowercase.
    timestamp = models.DateTimeField(primary_key=True)  # The composite primary key (timestamp, localityId) found, that is not supported. The first column is selected.
    r_mm_hr_field = models.FloatField(db_column='R(mm/hr)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    rain_index = models.BigIntegerField(blank=True, null=True)
    # id = models.I()

    class Meta:
        managed = False
        db_table = '"radar_data"."radar_data"'
        unique_together = (('timestamp', 'localityid'),)


class RadarSensorComparison(models.Model):
    localityid = models.ForeignKey(SiteConfigs,db_column='localityId',on_delete=models.CASCADE)  # Field name made lowercase.
    timestamp = models.DateTimeField(primary_key=True)
    radar_rain_index = models.BigIntegerField(blank=True, null=True)
    rdr_rain_intensity = models.FloatField(blank=True, null=True)
    sns_rain_intensity = models.TextField(blank=True, null=True)
    sns_rain_index = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"radar_data"."radar_sensor_comparison"'
        unique_together = (('timestamp', 'localityid'),)
