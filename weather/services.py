# services.py
import requests
import threading
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from .models import StationMeteo, ObservationMeteo
import logging

logger = logging.getLogger(__name__)


class WeatherDataService:
    """Service pour gérer les données météo"""
    
    @staticmethod
    def fahrenheit_to_celsius(f_temp):
        """Convertit Fahrenheit en Celsius"""
        if f_temp is None:
            return None
        return round((f_temp - 32) * 5/9, 1)
    
    @staticmethod
    def mph_to_kmh(mph):
        """Convertit mph en km/h"""
        if mph is None:
            return None
        return round(mph * 1.60934, 1)
    
    @staticmethod
    def inches_to_mm(inches):
        """Convertit inches en mm"""
        if inches is None:
            return None
        return round(inches * 25.4, 1)
    
    @staticmethod
    def incheshg_to_hpa(inches_hg):
        """Convertit inches Hg en hPa"""
        if inches_hg is None:
            return None
        return round(inches_hg * 33.8639, 1)
    
    @staticmethod
    def parse_datetime(date_string):
        """Convertit une chaîne de date en objet datetime"""
        try:
            return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                # Format avec timezone
                from dateutil import parser
                return parser.parse(date_string)
    
    @staticmethod
    def get_or_create_station(station_data):
        """Crée ou récupère une station météo"""
        station, created = StationMeteo.objects.get_or_create(
            station_id=station_data['stationID'],
            defaults={
                'latitude': station_data['lat'],
                'longitude': station_data['lon'],
                'timezone': station_data['tz'],
                'nom': f"Station {station_data['stationID']}"  # Nom par défaut
            }
        )
        
        if created:
            logger.info(f"Nouvelle station créée: {station.station_id}")
        
        return station
    
    @staticmethod
    def save_observation(observation_data):
        """Enregistre une observation météo"""
        try:
            with transaction.atomic():
                # Créer ou récupérer la station
                station = WeatherDataService.get_or_create_station(observation_data)
                
                # Vérifier si l'observation existe déjà (basé sur epoch)
                if ObservationMeteo.objects.filter(
                    station=station,
                    epoch=observation_data['epoch']
                ).exists():
                    logger.debug(f"Observation déjà existante pour epoch {observation_data['epoch']}")
                    return None
                
                # Créer l'observation
                imperial_data = observation_data.get('imperial', {})
                
                # Conversions vers le système métrique
                temp_high = WeatherDataService.fahrenheit_to_celsius(imperial_data.get('tempHigh'))
                temp_low = WeatherDataService.fahrenheit_to_celsius(imperial_data.get('tempLow'))
                temp_avg = WeatherDataService.fahrenheit_to_celsius(imperial_data.get('tempAvg'))
                
                windspeed_high = WeatherDataService.mph_to_kmh(imperial_data.get('windspeedHigh'))
                windspeed_low = WeatherDataService.mph_to_kmh(imperial_data.get('windspeedLow'))
                windspeed_avg = WeatherDataService.mph_to_kmh(imperial_data.get('windspeedAvg'))
                
                windgust_high = WeatherDataService.mph_to_kmh(imperial_data.get('windgustHigh'))
                windgust_low = WeatherDataService.mph_to_kmh(imperial_data.get('windgustLow'))
                windgust_avg = WeatherDataService.mph_to_kmh(imperial_data.get('windgustAvg'))
                
                dewpt_high = WeatherDataService.fahrenheit_to_celsius(imperial_data.get('dewptHigh'))
                dewpt_low = WeatherDataService.fahrenheit_to_celsius(imperial_data.get('dewptLow'))
                dewpt_avg = WeatherDataService.fahrenheit_to_celsius(imperial_data.get('dewptAvg'))
                
                windchill_high = WeatherDataService.fahrenheit_to_celsius(imperial_data.get('windchillHigh'))
                windchill_low = WeatherDataService.fahrenheit_to_celsius(imperial_data.get('windchillLow'))
                windchill_avg = WeatherDataService.fahrenheit_to_celsius(imperial_data.get('windchillAvg'))
                
                heatindex_high = WeatherDataService.fahrenheit_to_celsius(imperial_data.get('heatindexHigh'))
                heatindex_low = WeatherDataService.fahrenheit_to_celsius(imperial_data.get('heatindexLow'))
                heatindex_avg = WeatherDataService.fahrenheit_to_celsius(imperial_data.get('heatindexAvg'))
                
                pressure_max = WeatherDataService.incheshg_to_hpa(imperial_data.get('pressureMax'))
                pressure_min = WeatherDataService.incheshg_to_hpa(imperial_data.get('pressureMin'))
                
                precip_rate = WeatherDataService.inches_to_mm(imperial_data.get('precipRate'))
                precip_total = WeatherDataService.inches_to_mm(imperial_data.get('precipTotal'))
                
                observation = ObservationMeteo.objects.create(
                    station=station,
                    obs_time_utc=datetime.fromtimestamp(observation_data['epoch'], tz=timezone.utc),
                    obs_time_local=WeatherDataService.parse_datetime(observation_data['obsTimeLocal']),
                    epoch=observation_data['epoch'],
                    solar_radiation_high=observation_data.get('solarRadiationHigh'),
                    uv_high=observation_data.get('uvHigh'),
                    winddir_avg=observation_data.get('winddirAvg'),
                    humidity_high=observation_data.get('humidityHigh'),
                    humidity_low=observation_data.get('humidityLow'),
                    humidity_avg=observation_data.get('humidityAvg'),
                    qc_status=observation_data.get('qcStatus', -1),
                    
                    # Données converties en système métrique
                    temp_high=temp_high,
                    temp_low=temp_low,
                    temp_avg=temp_avg,
                    windspeed_high=windspeed_high,
                    windspeed_low=windspeed_low,
                    windspeed_avg=windspeed_avg,
                    windgust_high=windgust_high,
                    windgust_low=windgust_low,
                    windgust_avg=windgust_avg,
                    dewpt_high=dewpt_high,
                    dewpt_low=dewpt_low,
                    dewpt_avg=dewpt_avg,
                    windchill_high=windchill_high,
                    windchill_low=windchill_low,
                    windchill_avg=windchill_avg,
                    heatindex_high=heatindex_high,
                    heatindex_low=heatindex_low,
                    heatindex_avg=heatindex_avg,
                    pressure_max=pressure_max,
                    pressure_min=pressure_min,
                    pressure_trend=imperial_data.get('pressureTrend'),
                    precip_rate=precip_rate,
                    precip_total=precip_total
                )
                
                logger.info(f"Observation enregistrée: {station.station_id} - {observation.obs_time_local} - Temp: {temp_avg}°C")
                return observation
                
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'observation: {str(e)}")
            return None
    
    @staticmethod
    def save_observations_bulk(data):
        """Enregistre plusieurs observations en bloc"""
        if 'observations' not in data:
            logger.error("Format de données invalide: 'observations' manquant")
            return 0
        
        saved_count = 0
        for obs_data in data['observations']:
            if WeatherDataService.save_observation(obs_data):
                saved_count += 1
        
        logger.info(f"{saved_count} nouvelles observations enregistrées")
        return saved_count
    
    @staticmethod
    def get_temperature_stats(station_id, days=7):
        """Récupère les statistiques de température pour une station"""
        from django.db.models import Avg, Max, Min
        
        start_date = timezone.now() - timedelta(days=days)
        
        stats = ObservationMeteo.objects.filter(
            station__station_id=station_id,
            obs_time_utc__gte=start_date
        ).aggregate(
            avg_temp=Avg('temp_avg'),
            max_temp=Max('temp_high'),
            min_temp=Min('temp_low'),
            avg_humidity=Avg('humidity_avg')
        )
        
        return {
            'temp_moyenne': round(stats['avg_temp'] or 0, 1),
            'temp_maximale': round(stats['max_temp'] or 0, 1),
            'temp_minimale': round(stats['min_temp'] or 0, 1),
            'humidite_moyenne': round(stats['avg_humidity'] or 0, 1)
        }
    
    @staticmethod
    def get_latest_observation(station_id):
        """Récupère la dernière observation d'une station"""
        try:
            return ObservationMeteo.objects.filter(
                station__station_id=station_id
            ).order_by('-obs_time_utc').first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la dernière observation: {str(e)}")
            return None


class WeatherMonitorThread(threading.Thread):
    """Thread pour surveiller et enregistrer automatiquement les données météo"""
    
    def __init__(self, api_url, api_key, interval_seconds=900, station_id=None):
        """
        Args:
            api_url: URL de base l'API météo
            api_key: Clé API Weather.com
            interval_seconds: Intervalle de vérification en secondes (défaut: 5 minutes)
            station_id: ID de la station à surveiller (optionnel)
        """
        super().__init__(daemon=True)
        self.api_url = api_url
        self.api_key = api_key
        self.interval_seconds = interval_seconds
        self.station_id = station_id
        self.running = False
        self._stop_event = threading.Event()
    
    def run(self):
        """Démarre la surveillance"""
        self.running = True
        logger.info(f"Thread de surveillance démarré - Intervalle: {self.interval_seconds}s")
        
        while not self._stop_event.is_set():
            try:
                self.fetch_and_save_data()
            except Exception as e:
                logger.error(f"Erreur dans le thread de surveillance: {str(e)}")
            
            # Attendre avant la prochaine vérification
            self._stop_event.wait(self.interval_seconds)
        
        logger.info("Thread de surveillance arrêté")
    
    def fetch_and_save_data(self):
        """Récupère et enregistre les données depuis l'API"""
        try:
            # Construire l'URL avec les paramètres
            params = {
                'format': 'json',
                'units': 'e',  # Imperial units (nous convertissons en métrique)
                'apiKey': self.api_key
            }
            
            if self.station_id:
                params['stationId'] = self.station_id
            
            logger.debug(f"Récupération des données depuis: {self.api_url}")
            logger.debug(f"Paramètres: stationId={self.station_id}")
            
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            count = WeatherDataService.save_observations_bulk(data)
            
            if count > 0:
                # Récupérer la dernière température pour le log
                latest_obs = WeatherDataService.get_latest_observation(self.station_id)
                
                if latest_obs:
                    logger.info(f"✓ {count} nouvelles observations - Dernière temp: {latest_obs.temp_avg}°C")
                else:
                    logger.info(f"✓ {count} nouvelles observations enregistrées")
            else:
                logger.debug("Aucune nouvelle observation")
                
        except requests.RequestException as e:
            logger.error(f"Erreur de requête API: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}")
    
    def stop(self):
        """Arrête le thread proprement"""
        logger.info("Arrêt du thread de surveillance demandé...")
        self._stop_event.set()
        self.running = False


# Instance globale du thread de surveillance
_monitor_thread = None


def start_weather_monitoring(api_url, api_key, interval_seconds=300, station_id=None):
    """Démarre le thread de surveillance météo"""
    global _monitor_thread
    
    if _monitor_thread and _monitor_thread.running:
        logger.warning("Thread de surveillance déjà en cours d'exécution")
        return _monitor_thread
    
    _monitor_thread = WeatherMonitorThread(api_url, api_key, interval_seconds, station_id)
    _monitor_thread.start()
    
    logger.info(f"✓ Surveillance météo démarrée: {station_id} (intervalle: {interval_seconds}s)")
    return _monitor_thread


def stop_weather_monitoring():
    """Arrête le thread de surveillance météo"""
    global _monitor_thread
    
    if _monitor_thread:
        _monitor_thread.stop()
        _monitor_thread = None
        logger.info("✓ Surveillance météo arrêtée")


def get_temperature_conversion(fahrenheit):
    """Fonction utilitaire pour convertir Fahrenheit en Celsius"""
    return WeatherDataService.fahrenheit_to_celsius(fahrenheit)


def get_windspeed_conversion(mph):
    """Fonction utilitaire pour convertir mph en km/h"""
    return WeatherDataService.mph_to_kmh(mph)


def get_weather_stats(station_id, days=7):
    """Récupère les statistiques météo pour une station"""
    return WeatherDataService.get_temperature_stats(station_id, days)


def get_latest_weather(station_id):
    """Récupère la dernière observation météo pour une station"""
    return WeatherDataService.get_latest_observation(station_id)