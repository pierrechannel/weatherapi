# views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min, Count
import json
import logging

from .models import StationMeteo, ObservationMeteo
from .services import WeatherDataService, start_weather_monitoring, stop_weather_monitoring

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def receive_weather_data(request):
    """
    Endpoint pour recevoir les données météo de la station
    POST /api/weather/receive/
    """
    try:
        data = json.loads(request.body)
        count = WeatherDataService.save_observations_bulk(data)
        
        return JsonResponse({
            'status': 'success',
            'message': f'{count} observations enregistrées',
            'count': count
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Format JSON invalide'
        }, status=400)
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_daily_observations(request, station_id):
    """
    Récupère les observations journalières d'une station
    GET /api/weather/daily/<station_id>/?date=YYYY-MM-DD
    """
    try:
        # Récupérer la date (par défaut aujourd'hui)
        date_str = request.GET.get('date')
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = timezone.now().date()
        
        # Récupérer la station
        try:
            station = StationMeteo.objects.get(station_id=station_id)
        except StationMeteo.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'Station {station_id} non trouvée'
            }, status=404)
        
        # Récupérer les observations du jour
        observations = ObservationMeteo.objects.filter(
            station=station,
            obs_time_local__date=target_date
        ).order_by('obs_time_local')
        
        # Calculer les statistiques
        stats = observations.aggregate(
            temp_avg=Avg('temp_avg'),
            temp_max=Max('temp_high'),
            temp_min=Min('temp_low'),
            humidity_avg=Avg('humidity_avg'),
            precip_total=Max('precip_total'),
            wind_max=Max('windspeed_high'),
            count=Count('id')
        )
        
        # Formater les données
        data = {
            'station_id': station_id,
            'date': target_date.isoformat(),
            'statistics': {
                'temperature_avg': round(stats['temp_avg'], 1) if stats['temp_avg'] else None,
                'temperature_max': stats['temp_max'],
                'temperature_min': stats['temp_min'],
                'humidity_avg': round(stats['humidity_avg'], 1) if stats['humidity_avg'] else None,
                'precipitation_total': stats['precip_total'],
                'wind_speed_max': stats['wind_max'],
                'observation_count': stats['count']
            },
            'observations': [
                {
                    'time_utc': obs.obs_time_utc.isoformat(),
                    'time_local': obs.obs_time_local.strftime('%Y-%m-%d %H:%M:%S'),
                    'temperature': {
                        'high': obs.temp_high,
                        'low': obs.temp_low,
                        'avg': obs.temp_avg
                    },
                    'humidity': {
                        'high': obs.humidity_high,
                        'low': obs.humidity_low,
                        'avg': obs.humidity_avg
                    },
                    'wind': {
                        'direction': obs.winddir_avg,
                        'speed_high': obs.windspeed_high,
                        'speed_avg': obs.windspeed_avg,
                        'gust_high': obs.windgust_high
                    },
                    'pressure': {
                        'max': obs.pressure_max,
                        'min': obs.pressure_min,
                        'trend': obs.pressure_trend
                    },
                    'precipitation': {
                        'rate': obs.precip_rate,
                        'total': obs.precip_total
                    },
                    'solar_radiation': obs.solar_radiation_high,
                    'uv_index': obs.uv_high
                }
                for obs in observations
            ]
        }
        
        return JsonResponse(data, safe=False)
        
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def list_stations(request):
    """
    Liste toutes les stations météo
    GET /api/weather/stations/
    """
    stations = StationMeteo.objects.all()
    
    data = [
        {
            'station_id': station.station_id,
            'nom': station.nom,
            'latitude': station.latitude,
            'longitude': station.longitude,
            'timezone': station.timezone,
            'observation_count': station.observations.count(),
            'last_observation': station.observations.first().obs_time_local.isoformat() 
                               if station.observations.exists() else None
        }
        for station in stations
    ]
    
    return JsonResponse(data, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def start_monitoring(request):
    """
    Démarre le thread de surveillance automatique
    POST /api/weather/monitoring/start/
    Body: {"api_url": "...", "interval_seconds": 300, "station_id": "..."}
    """
    try:
        data = json.loads(request.body)
        api_url = data.get('api_url')
        interval = data.get('interval_seconds', 300)
        station_id = data.get('station_id')
        
        if not api_url:
            return JsonResponse({
                'status': 'error',
                'message': 'api_url requis'
            }, status=400)
        
        thread = start_weather_monitoring(api_url, interval, station_id)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Surveillance démarrée',
            'interval_seconds': interval
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def stop_monitoring(request):
    """
    Arrête le thread de surveillance automatique
    POST /api/weather/monitoring/stop/
    """
    stop_weather_monitoring()
    return JsonResponse({
        'status': 'success',
        'message': 'Surveillance arrêtée'
    })


def dashboard(request):
    """Vue du tableau de bord"""
    stations = StationMeteo.objects.all()
    
    # Récupérer les statistiques pour chaque station
    station_data = []
    for station in stations:
        today = timezone.now().date()
        observations_today = ObservationMeteo.objects.filter(
            station=station,
            obs_time_local__date=today
        )
        
        latest_obs = station.observations.first()
        
        station_data.append({
            'station': station,
            'observations_today': observations_today.count(),
            'latest_observation': latest_obs,
            'total_observations': station.observations.count()
        })
    
    context = {
        'stations': station_data,
        'total_stations': stations.count()
    }
    
    return render(request, 'weather/dashboard.html', context)