from django.shortcuts import render
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.http import JsonResponse
import geopandas as gpd
from shapely.geometry import Point
from shapely import centroid, Polygon
from sklearn.metrics import accuracy_score

# Create your views here.
from .models import SiteConfigs,Forecast,RadarSensorComparison

def get_forecasted_sites():
    selected_sites = Forecast.objects.order_by('localityid').distinct('localityid')
    return selected_sites.values_list('localityid')


def round_by_round_function(dt):
    round_to = 15
    seconds = (dt - dt.min).seconds
    rounded_seconds = round(seconds / (round_to * 60)) * (round_to * 60)
    rounded_time = dt + timedelta(0, rounded_seconds - seconds, -dt.microsecond)
    if rounded_time > datetime.now():
        return rounded_time - timedelta(minutes=15)
    else:
        return rounded_time
# original_time = datetime(2023, 3, 10, 14, 21)
# rounded_time = print(round_by_round_function(original_time),"Hello")


def home_screen(request):
    # available_sites = pd.DataFrame.from_records(get_active_sites())
    # print(available_sites)
    forecasted_sites = get_forecasted_sites()
    # print(forecasted_sites)
    site_details = SiteConfigs.objects.filter(localityid__in=forecasted_sites).all().values()
    site_details = pd.DataFrame.from_records(site_details)
    city_names = list(site_details['cityname'].unique())
    latest_timestamp = round_by_round_function(datetime.now())
    max_timestamp = latest_timestamp - timedelta(days=30)
    radar_weather_data = RadarSensorComparison.objects.filter(timestamp__gte=max_timestamp).values()
    radar_weather_data = pd.DataFrame.from_records(radar_weather_data).sort_values('timestamp',ascending=False)

    overall_accuracy = accuracy_score(y_true=radar_weather_data['radar_rain_index'],y_pred=radar_weather_data['sns_rain_index'])
    overall_accuracy = round(overall_accuracy * 100,2)

    inactive_sensors = radar_weather_data['sns_rain_intensity'].isna().sum()
    active_sensors = len(radar_weather_data) - inactive_sensors
    # print(inactive_sensors,len(radar_weather_data))
    perc_active = round((active_sensors * 100 / len(radar_weather_data)),2)
    return render(request=request,template_name='home.html',context={'cities':city_names,'overall_accuracy':overall_accuracy,'perc_active':perc_active})


def get_city_weather_forecast(request):
        # print(request.GET['city'])
        if request.method == 'GET':
            city = request.GET['city']
            print(city)
            latest_timestamp = round_by_round_function(datetime.now())
            max_timestamp = latest_timestamp - timedelta(days=30)
            ## get forecasted data
            #forecast_data = Forecast.objects.filter(cityname=city).values('rain_intensity','rain_index','localityname','timestamp','localityid','latitude','longitude')
            #forecast_data = pd.DataFrame.from_records(forecast_data).sort_values('timestamp')
            #single_target = forecast_data.loc[forecast_data['timestamp']==latest_timestamp,:]
            unique_localityId = SiteConfigs.objects.filter(cityname=city).values('localityid','localityname','latitude','longitude','device_type')
            unique_localityId = pd.DataFrame.from_records(unique_localityId)
            #
            radar_weather_data = RadarSensorComparison.objects.filter(timestamp__gte=max_timestamp).filter(localityid__in = unique_localityId['localityid']).values()
            radar_weather_data = pd.DataFrame.from_records(radar_weather_data).sort_values('timestamp',ascending=False)
            cntre = centroid(Polygon(unique_localityId.loc[:,['longitude','latitude']].to_numpy()))

            # print(radar_weather_data.columns)
            radar_weather_data = radar_weather_data.merge(unique_localityId,right_on='localityid',left_on='localityid_id').sort_values('timestamp',ascending=False)
            overall_accuracy = accuracy_score(y_true=radar_weather_data['radar_rain_index'],y_pred=radar_weather_data['sns_rain_index'])
            overall_accuracy = round(overall_accuracy * 100,2)
            end_show_timestamp = latest_timestamp + timedelta(minutes=60)
            end_radar_timestamp = latest_timestamp - timedelta(minutes=60)

            one_month_date = latest_timestamp - timedelta(days=30)
            real_time = latest_timestamp - timedelta(hours=24)
            one_month_data = radar_weather_data.loc[radar_weather_data['timestamp']>=one_month_date,:]
            real_time_data = radar_weather_data.loc[radar_weather_data['timestamp']>=real_time,:]

            # print(real_time_data)
            real_time_accuracy = round(accuracy_score(y_pred=real_time_data['sns_rain_index'],y_true=real_time_data['radar_rain_index']) * 100,2)
            one_month_accuracy = round(accuracy_score(y_pred=one_month_data['sns_rain_index'],y_true=one_month_data['radar_rain_index']) * 100,2)

            missing_sensors = radar_weather_data['sns_rain_intensity'].isna().sum()
            overall_sensors = len(radar_weather_data)
            active_sensors = overall_sensors - missing_sensors
            sensor_activeness = round(active_sensors/overall_sensors*100,2)
            print(sensor_activeness)
            return JsonResponse({'single_target':unique_localityId.loc[unique_localityId['device_type']=='2 - Rain gauge system'].to_dict('records'),
                                 'send_df':real_time_data.to_dict('records'),'x':cntre.x,'y':cntre.y,'real_time_accuracy':real_time_accuracy,
                                 'one_month_accuracy':one_month_accuracy,'sensor_active':sensor_activeness,'overall_accuracy':overall_accuracy})



            # radar_data = RadarData.objects.filter(localityid__in=unique_localityId['localityid']).values('r_mm_hr_field','rain_index',
                                                                                        #    'timestamp','localityid')
            # radar_data = pd.DataFrame.from_records(radar_data).sort_values('timestamp',ascending=False)
            # print(radar_data)
            # radar_data = radar_data.rename(columns={'r_mm_hr_field':'radar_rain_intensity','rain_index':'radar_rain_index'})
            # weather_data = WeatherData.objects.filter(location_id__in=unique_localityId['localityid']).values('rain_intensity','rain_index','timestamp',
            #                                                                                                  'location_id')

            # weather_data = pd.DataFrame.from_records(weather_data).sort_values('timestamp',ascending=True)
            # weather_data = weather_data.rename(columns={'location_id':'localityid','sns_rain_intensity':'rain_intensity','sns_rain_index':'rain_index'})

            # # print(weather_data)
            # send_df = radar_data.merge(weather_data,on=['timestamp','localityid'])
            # send_df = send_df.merge(unique_localityId,on='localityid')
            # print(send_df)
