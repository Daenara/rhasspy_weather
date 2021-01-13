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


def parse_condition_intent(slots: List) -> WeatherRequest:
    """
    Parses rhasspy condition weather intent.

    Args:
        slots: the slot list contained in an NluIntent

    Returns: WeatherRequest object

    """
    locale = get_config().locale
    new_request = parse_general_intent(slots)

    new_request.forecast_type = ForecastType.CONDITION
    for slot in slots:
        if slot.slot_name == slot_names["condition"]:
            new_request.requested = parse_condition(slot.value["value"], locale)
    return new_request


def parse_item_intent(slots: List) -> WeatherRequest:
    """
    Parses rhasspy item weather intent

    Args:
        slots: the slot list contained in an NluIntent

    Returns: WeatherRequest object

    """
    locale = get_config().locale
    new_request = parse_general_intent(slots)

    new_request.forecast_type = ForecastType.ITEM
    for slot in slots:
        if slot.slot_name == slot_names["item"]:
            new_request.requested = parse_item(slot.value["value"], locale)
    return new_request


def parse_temperature_intent(slots: List) -> WeatherRequest:
    """
    Parses rhasspy temperature weather intent

    Args:
        slots: the slot list contained in an NluIntent

    Returns: WeatherRequest object

    """
    locale = get_config().locale
    new_request = parse_general_intent(slots)

    new_request.forecast_type = ForecastType.TEMPERATURE
    for slot in slots:
        if slot.slot_name == slot_names["temperature"]:
            new_request.requested = parse_temperature(slot.value["value"], locale)
    return new_request
