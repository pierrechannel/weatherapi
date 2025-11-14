from django.core.management.base import BaseCommand
from weather.services import WeatherService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch and save weather data if changes detected'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force fetch even if no changes detected',
        )
    
    def handle(self, *args, **options):
        force_fetch = options['force']
        
        if force_fetch or WeatherService.should_fetch_automatically():
            self.stdout.write("Fetching weather data...")
            result = WeatherService.fetch_and_save_if_changed()
            
            if result['status'] == 'success':
                if result.get('saved', False):
                    self.stdout.write(
                        self.style.SUCCESS(f"Success: {result['message']}")
                    )
                    self.stdout.write(f"Temperature: {result['data']['temperature']}°F")
                else:
                    self.stdout.write(f"Info: {result['message']}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"Error: {result['message']}")
                )
        else:
            self.stdout.write("Skipping fetch - last observation is recent")