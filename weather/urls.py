# urls.py
from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # API endpoints
    path('api/receive/', views.receive_weather_data, name='receive_data'),
    path('api/daily/<str:station_id>/', views.get_daily_observations, name='daily_observations'),
    path('api/stations/', views.list_stations, name='list_stations'),
    
    # Monitoring
    path('api/monitoring/start/', views.start_monitoring, name='start_monitoring'),
    path('api/monitoring/stop/', views.stop_monitoring, name='stop_monitoring'),
]