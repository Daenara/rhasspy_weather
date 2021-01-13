import logging

from rhasspy_weather.data_types.request import WeatherRequest
from rhasspy_weather.parser import rhasspy_intent
from rhasspyhermes.nlu import NluIntent

log = logging.getLogger(__name__)

# if you changed the slot names in rhasspy, change them here on the right side
slot_names = {
    "day": "when_day",
    "time": "when_time",
    "location": "location",
    "item": "item",
    "condition": "condition",
    "temperature": "temperature"
}


def parse_intent_message(intent_message: NluIntent) -> WeatherRequest:
    """
    Parses any of the rhasspy weather intents.

    Args:
        intent_message: a Hermes NluIntent

    Returns: WeatherRequest object

    """
    return rhasspy_intent.parse_intent_message(intent_message.to_rhasspy_dict())

    return new_request

def get_template_values(intent_message: NluIntent) -> dict:
    return rhasspy_intent.get_template_values(intent_message.to_rhasspy_dict())
