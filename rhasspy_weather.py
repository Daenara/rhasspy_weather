# -*- encoding: utf-8 -*-
from rhasspy_weather.forecast import WeatherForecast
from rhasspy_weather.report import WeatherReport
from rhasspy_weather.config import WeatherConfig
import rhasspy_weather.parser.rhasspy_intent as parser
import logging

log = logging.getLogger(__name__)

# function being called when snips detects an intent related to the weather
def get_weather_forecast(intent_message):
    log.info("Loading Config")
    config = WeatherConfig()
    if config.status.is_error:
        return config.status.status_response()
    
    log.info("Parsing rhasspy intent")
    request = parser.parse_intent_message(intent_message, config)
    if request.status.is_error:
        return request.status.status_response()
    
    log.info("Requesting weather")
    if config.api == "openweathermap":
        import rhasspy_weather.api.openweathermap as api
    forecast = api.get_weather(request.location, config)
    if forecast.status.is_error:
        return forecast.status.status_response()
    
    log.info("Formulating answer")
    response = WeatherReport(request, forecast, config).generate_report()
    
    return response
