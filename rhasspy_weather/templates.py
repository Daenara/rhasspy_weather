import datetime
import json
import logging
from enum import Enum
from string import Template


from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.location import Location
from rhasspy_weather.data_types.error import WeatherError

log = logging.getLogger(__name__)

# TODO: add more detailed templates to use (especially debug/expanded to use with testcases)
# TODO: move intent_to_template to parser and call it from there


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
    if "rhasspy_intent" in config.parser.__name__:
        template_values = {**template_values, **intent_to_template_values(weather_input)}

    output = template.safe_substitute(template_values)
    if "\n" in output and remove_not_replaced_lines:
        output_array = output.splitlines()
        new_output = ""
        for item in output_array:
            if "$" in item:
                pass
            else:
                if new_output is "":
                    new_output = item
                else:
                    new_output = new_output + "\n" + item
        output = new_output
    if ".json" in config.output_template_name and template_override is None:
        output = output.replace("None", "null").replace("'", "\"")
        # TODO: test this with the next version of rhasspy where json.loads is set to ensure_ascii=False, might be unnecessary then
        output = json.dumps(json.loads(output, ensure_ascii=False))  # not the best way but otherwise the json is not correct
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


__report = None


def weather_report_to_template_values(report):
    global __report
    if __report is None:
        __report = report.generate_report()
    template_values = {
        "weather_text": __report
    }
    return template_values


def weather_error_to_template_values(error):
    template_values = {
        "weather_text": error.message
    }
    return template_values


def weather_object_to_template_values(weather_object, name):
    template_values = {}
    for key, value in weather_object.__dict__.items():
        new_key = name + "_" + key.replace("_"+ type(weather_object).__name__ + "__", "")
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
    return template_values

