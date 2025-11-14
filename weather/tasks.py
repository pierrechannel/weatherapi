from weatherapi.celery import shared_task
from .services import WeatherService
import logging

logger = logging.getLogger(__name__)

@shared_task
def fetch_weather_task():
    """Celery task to fetch weather data every 5 minutes"""
    logger.info("Starting weather fetch task")
    result = WeatherService.fetch_and_save_if_changed()
    logger.info(f"Weather fetch task completed: {result['message']}")
    return result
