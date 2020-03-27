# -*- encoding: utf-8 -*-
from .data_types.forecast import WeatherForecast
from .data_types.report import WeatherReport
from .data_types.config import WeatherConfig
import logging

log = logging.getLogger(__name__)

# function being called when snips detects an intent related to the weather
def get_weather_forecast(intent_message):
    log.info("Loading Config")
    config = WeatherConfig()
    if config.status.is_error:
        return config.status.status_response()
    
    log.info("Parsing rhasspy intent")
    request = config.parser.parse_intent_message(intent_message, config)
    if request.status.is_error:
        return request.status.status_response()
    
    log.info("Requesting weather")
    forecast = config.api.get_weather(request.location, config)
    if forecast.status.is_error:
        return forecast.status.status_response()
    
    log.info("Formulating answer")
    response = WeatherReport(request, forecast, config).generate_report()
    
    return response
