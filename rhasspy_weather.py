# -*- encoding: utf-8 -*-
import logging

import rhasspy_weather.globals
from .data_types.config import WeatherConfig
from .data_types.report import WeatherReport

log = logging.getLogger(__name__)


# function being called when snips detects an intent related to the weather
def get_weather_forecast(intent_message):
    log.info("Loading Config")
    rhasspy_weather.globals.config = WeatherConfig()
    config = rhasspy_weather.globals.config

    if config.status.is_error:
        return config.status.status_response()

    log.info("Parsing rhasspy intent")
    request = config.parser.parse_intent_message(intent_message)
    if request.status.is_error:
        return request.status.status_response()

    log.info("Requesting weather")
    forecast = config.api.get_weather(request.location)
    if forecast.status.is_error:
        return forecast.status.status_response()

    log.info("Formulating answer")
    response = WeatherReport(request, forecast).generate_report()

    return response
