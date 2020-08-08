import logging
from string import Template

from rhasspy_weather.data_types.config import get_config

log = logging.getLogger(__name__)


def fill_template(intent_message, report):
    config = get_config()
    template = Template(config.output_template)
    template_values = {**intent_to_template_values(intent_message), **weather_report_to_template_values(report)}
    output = template.safe_substitute(template_values)
    output = output.replace("None", "null").replace("'", "\"")
    return output


def intent_to_template_values(intent_message):
    template_values = {}
    for key, value in intent_message.items():
        if key == "intent":
            for i_key, i_value in value.items():
                template_values["intent_"+i_key] = i_value
        else:
            template_values["intent_" + key] = value
    return template_values


def weather_report_to_template_values(report):
    template_values = {
        "weather_text": report.generate_report()
    }
    return template_values
