# models.py
from django.db import models
from django.utils import timezone

class StationMeteo(models.Model):
    station_id = models.CharField(max_length=50, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timezone = models.CharField(max_length=50)
    nom = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Station Météo"
        verbose_name_plural = "Stations Météo"
    
    def __str__(self):
        return f"{self.station_id} ({self.nom or 'Sans nom'})"


class ObservationMeteo(models.Model):
    station = models.ForeignKey(StationMeteo, on_delete=models.CASCADE, related_name='observations')
    
    # Informations temporelles
    obs_time_utc = models.DateTimeField()
    obs_time_local = models.DateTimeField()
    epoch = models.BigIntegerField()
    
    # Données environnementales
    solar_radiation_high = models.IntegerField(null=True, blank=True)
    uv_high = models.IntegerField(null=True, blank=True)
    winddir_avg = models.IntegerField(null=True, blank=True)
    
    # Humidité
    humidity_high = models.IntegerField(null=True, blank=True)
    humidity_low = models.IntegerField(null=True, blank=True)
    humidity_avg = models.IntegerField(null=True, blank=True)
    
    # Températures (Imperial - Fahrenheit)
    temp_high = models.FloatField(null=True, blank=True)
    temp_low = models.FloatField(null=True, blank=True)
    temp_avg = models.FloatField(null=True, blank=True)
    
    # Vent
    windspeed_high = models.FloatField(null=True, blank=True)
    windspeed_low = models.FloatField(null=True, blank=True)
    windspeed_avg = models.FloatField(null=True, blank=True)
    
    windgust_high = models.FloatField(null=True, blank=True)
    windgust_low = models.FloatField(null=True, blank=True)
    windgust_avg = models.FloatField(null=True, blank=True)
    
    # Point de rosée
    dewpt_high = models.FloatField(null=True, blank=True)
    dewpt_low = models.FloatField(null=True, blank=True)
    dewpt_avg = models.FloatField(null=True, blank=True)
    
    # Température ressentie
    windchill_high = models.FloatField(null=True, blank=True)
    windchill_low = models.FloatField(null=True, blank=True)
    windchill_avg = models.FloatField(null=True, blank=True)
    
    heatindex_high = models.FloatField(null=True, blank=True)
    heatindex_low = models.FloatField(null=True, blank=True)
    heatindex_avg = models.FloatField(null=True, blank=True)
    
    # Pression
    pressure_max = models.FloatField(null=True, blank=True)
    pressure_min = models.FloatField(null=True, blank=True)
    pressure_trend = models.FloatField(null=True, blank=True)
    
    # Précipitations
    precip_rate = models.FloatField(null=True, blank=True)
    precip_total = models.FloatField(null=True, blank=True)
    
    # QC Status
    qc_status = models.IntegerField(default=-1)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Observation Météo"
        verbose_name_plural = "Observations Météo"
        ordering = ['-obs_time_utc']
        unique_together = ['station', 'epoch']  # Éviter les doublons
    
    def __str__(self):
        return f"{self.station.station_id} - {self.obs_time_local}"