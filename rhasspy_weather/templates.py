import datetime
import json
import logging
from enum import Enum
from string import Template


from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.location import Location
from rhasspy_weather.data_types.error import WeatherError
from rhasspy_weather.data_types.report import WeatherReport

log = logging.getLogger(__name__)

# TODO: add more detailed templates to use (especially debug/expanded to use with testcases)


def fill_template(weather_input, result, template_override=None, remove_not_replaced_lines=True):
    config = get_config()
    if template_override is None:
        template = Template(config.output_template)
    else:
        template = Template(template_override)
    template_values = {}
    if type(result) == WeatherError:
        template_values = {**template_values, **weather_error_to_template_values(result)}
    else:
        template_values = {**template_values, **weather_report_to_template_values(result), **weather_object_to_template_values(result.request, "request")}
    template_values = {**template_values, **config.parser.get_template_values(weather_input)}
    output = template.safe_substitute(template_values)
    if "\n" in output and remove_not_replaced_lines:
        output_array = output.splitlines()
        new_output = ""
        for item in output_array:
            if "$" in item:
                pass
            else:
                if new_output == "":
                    new_output = item
                else:
                    new_output = new_output + "\n" + item
        output = new_output
    if ".json" in config.output_template_name and template_override is None:
        output = output.replace("None", "null").replace("'", "\"")
        output = json.dumps(json.loads(output), ensure_ascii=False)  # not the best way but otherwise the json is not correct
    return output


__template_values = {}
__report_speech = None


def weather_report_to_template_values(report: WeatherReport) -> dict:
    global __report_speech
    if __report_speech is None or __report_speech != report.speech[report.request.forecast_type]:
        __report_speech = report.speech[report.request.forecast_type]
    template_values = {
        "speech": __report_speech
    }
    template_values = {**template_values, ** weather_object_to_template_values(report, "report")}
    return template_values


def weather_error_to_template_values(error: WeatherError) -> dict:
    template_values = {
        "speech": error.message
    }
    return template_values


def weather_object_to_template_values(weather_object, name) -> dict:
    global __template_values
    if name not in __template_values:
        __template_values[name] = {}
        for key, value in weather_object.__dict__.items():
            new_key = name + "_" + key.replace("_" + type(weather_object).__name__ + "__", "")
            if isinstance(value, str) and not value == "":
                __template_values[name][new_key] = value
            elif isinstance(value, bool):
                __template_values[name][new_key] = value
            elif isinstance(value, int):
                __template_values[name][new_key] = value
            elif isinstance(value, float):
                __template_values[name][new_key] = value
            elif isinstance(value, Enum):
                __template_values[name][new_key] = str(value)
            elif isinstance(value, datetime.time) or isinstance(value, datetime.date):
                __template_values[name][new_key] = str(value)
            elif isinstance(value, Location):
                for l_key, l_value in value.__dict__.items():
                    new_l_key = new_key + "_" + l_key
                    __template_values[name][new_l_key] = l_value
    return __template_values[name]

