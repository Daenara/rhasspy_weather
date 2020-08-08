import datetime
import logging
from enum import Enum
from string import Template


from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.location import Location
from rhasspy_weather.data_types.status import Status

log = logging.getLogger(__name__)


def fill_template(intent_message, report):
    config = get_config()
    log.debug(type(config.parser))
    log.debug(config.parser.__name__)
    template = Template(config.output_template)
    rhasspy_intent_values = {}
    weather_report_values = weather_report_to_template_values(report)
    weather_request_values = weather_request_to_template_values(report.request)
    if "rhasspy_intent" in config.parser.__name__:
        rhasspy_intent_values = intent_to_template_values(intent_message)
    template_values = {**rhasspy_intent_values, **weather_report_values, **weather_request_values}
    output = template.safe_substitute(template_values)
    output = output.replace("None", "null").replace("'", "\"")
    return output


def intent_to_template_values(intent_message):
    template_values = {}
    for key, value in intent_message.items():
        if key == "intent":
            for i_key, i_value in value.items():
                template_values["intent_" + i_key] = i_value
        else:
            template_values["intent_" + key] = value
    return template_values


def weather_report_to_template_values(report):
    template_values = {
        "weather_text": report.generate_report()
    }
    return template_values


def weather_request_to_template_values(request):
    template_values = {}
    for key, value in request.__dict__.items():
        new_key = "request_" + key.replace("_WeatherRequest__", "")
        if isinstance(value, str) and not value == "":
            template_values[new_key] = value
        elif isinstance(value, bool):
            template_values[new_key] = value
        elif isinstance(value, Enum):
            template_values[new_key] = str(value)
        elif isinstance(value, datetime.time) or isinstance(value, datetime.date):
            template_values[new_key] = str(value)
        elif isinstance(value, Location):
            for l_key, l_value in value.__dict__.items():
                new_l_key = new_key + "_" + l_key
                template_values[new_l_key] = l_value
        elif isinstance(value, Status):
            template_values[new_key] = str(value.status_code)
    return template_values

