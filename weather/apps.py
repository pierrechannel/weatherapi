# weather/apps.py
from django.apps import AppConfig
import os


class WeatherConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'weather'
    
    def ready(self):
        """
        Démarre automatiquement le thread de surveillance au démarrage de Django
        """
        # Éviter le double chargement en mode debug
        if os.environ.get('RUN_MAIN') == 'true' or os.environ.get('RUN_MAIN') is None:
            from .services import start_weather_monitoring
            
            # Configuration de la surveillance (VALEURS EN DUR)
            API_URL = 'https://api.weather.com/v2/pws/observations/all/1day'
            API_KEY = 'df904ffa7aad495d904ffa7aadb95d3b'
            
            INTERVAL = 900  # 15 minutes
            STATION_ID = 'IBUJUM3'
            
            # Démarrer la surveillance automatique
            try:
                start_weather_monitoring(
                    api_url=API_URL,
                    api_key=API_KEY,
                    interval_seconds=INTERVAL,
                    station_id=STATION_ID
                )
                print(f"✓ Surveillance météo démarrée: {STATION_ID} (intervalle: {INTERVAL}s)")
                print(f"✓ API URL: {API_URL}")
            except Exception as e:
                print(f"✗ Erreur démarrage surveillance météo: {e}")