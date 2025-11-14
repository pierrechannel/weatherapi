# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import StationMeteo, ObservationMeteo


@admin.register(StationMeteo)
class StationMeteoAdmin(admin.ModelAdmin):
    list_display = ['station_id', 'nom', 'latitude', 'longitude', 'timezone', 'observations_count', 'derniere_observation']
    search_fields = ['station_id', 'nom']
    list_filter = ['timezone']
    
    def observations_count(self, obj):
        return obj.observations.count()
    observations_count.short_description = 'Nb Observations'
    
    def derniere_observation(self, obj):
        derniere = obj.observations.first()
        if derniere:
            return derniere.obs_time_local
        return '-'
    derniere_observation.short_description = 'Dernière Obs'


@admin.register(ObservationMeteo)
class ObservationMeteoAdmin(admin.ModelAdmin):
    list_display = [
        'station', 'obs_time_local', 'temp_avg_display', 
        'humidity_avg', 'windspeed_avg', 'precip_total', 'qc_status_display'
    ]
    list_filter = ['station', 'obs_time_local', 'qc_status']
    search_fields = ['station__station_id']
    date_hierarchy = 'obs_time_local'
    readonly_fields = ['created_at', 'updated_at', 'epoch']
    
    fieldsets = (
        ('Informations Station', {
            'fields': ('station', 'obs_time_utc', 'obs_time_local', 'epoch', 'qc_status')
        }),
        ('Température (°F)', {
            'fields': ('temp_high', 'temp_low', 'temp_avg', 'dewpt_high', 'dewpt_low', 'dewpt_avg'),
            'classes': ('collapse',)
        }),
        ('Température Ressentie (°F)', {
            'fields': (
                'windchill_high', 'windchill_low', 'windchill_avg',
                'heatindex_high', 'heatindex_low', 'heatindex_avg'
            ),
            'classes': ('collapse',)
        }),
        ('Humidité (%)', {
            'fields': ('humidity_high', 'humidity_low', 'humidity_avg'),
        }),
        ('Vent', {
            'fields': (
                'winddir_avg',
                'windspeed_high', 'windspeed_low', 'windspeed_avg',
                'windgust_high', 'windgust_low', 'windgust_avg'
            ),
            'classes': ('collapse',)
        }),
        ('Pression & Précipitations', {
            'fields': (
                'pressure_max', 'pressure_min', 'pressure_trend',
                'precip_rate', 'precip_total'
            ),
        }),
        ('Radiation & UV', {
            'fields': ('solar_radiation_high', 'uv_high'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def temp_avg_display(self, obj):
        if obj.temp_avg:
            return format_html('<strong>{}°F</strong>', obj.temp_avg)
        return '-'
    temp_avg_display.short_description = 'Temp Moy'
    
    def qc_status_display(self, obj):
        if obj.qc_status == -1:
            return format_html('<span style="color: orange;">⚠ Non vérifié</span>')
        elif obj.qc_status == 1:
            return format_html('<span style="color: green;">✓ Validé</span>')
        else:
            return format_html('<span style="color: red;">✗ Erreur</span>')
    qc_status_display.short_description = 'Statut QC'