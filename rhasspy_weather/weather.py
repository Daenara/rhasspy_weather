# -*- encoding: utf-8 -*-
import logging

from rhasspy_weather.data_types.report import WeatherReport
from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.error import WeatherError
from rhasspy_weather.templates import fill_template

log = logging.getLogger(__name__)

# TODO: find a better name for this file


# function being called when rhasspy detects an intent related to the weather
def get_weather_forecast(intent_message):
    config = get_config()

    if config is None or config.error:
        return "Configuration could not be read. Please make sure everything is set up correctly"

    try:
        log.info("Parsing rhasspy intent")
        request = config.parser.parse_intent_message(intent_message)

        log.info("Requesting weather")
        forecast = config.api.get_weather(request.location)

        log.info("Formulating answer")
        report = WeatherReport(request, forecast)

        log.info("Answering question")
        filled_template = fill_template(intent_message, report)
        config.output.output_response(filled_template)
    except WeatherError as error:
        filled_template = fill_template(intent_message, error)
        config.output.output_response(filled_template)

    return filled_template
