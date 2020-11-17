import datetime
import logging
from typing import List

from rhasspy_weather.data_types.request import WeatherRequest, DateType, ForecastType, Grain
from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.utils.parser import parse_date, parse_time, parse_condition, parse_temperature, parse_item, \
    parse_location
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
    if "GetWeatherForecastCondition" == intent_message.intent.intent_name:
        return parse_condition_intent(intent_message.slots)
    elif "GetWeatherForecastItem" == intent_message.intent.intent_name:
        return parse_item_intent(intent_message.slots)
    elif "GetWeatherForecastTemperature" == intent_message.intent.intent_name:
        return parse_temperature_intent(intent_message.slots)

    return parse_general_intent(intent_message.slots)


def parse_general_intent(slots: List) -> WeatherRequest:
    """
    Parses general rhasspy weather intents.

    Args:
        slots: the slot list contained in an NluIntent

    Returns: WeatherRequest object

    """
    config = get_config()
    today = datetime.datetime.now(config.timezone).date()

    # define default request
    new_request = WeatherRequest(DateType.FIXED, Grain.DAY, today, ForecastType.FULL)
    used_slots = []
    for slot in slots:
        if slot.value["value"] is not "":
            if slot.slot_name == slot_names["day"]:
                new_request.request_date, new_request.date_specified = parse_date(slot.value["value"], config.locale)
                used_slots.append(slot)

            if slot.slot_name == slot_names["time"]:
                time, str_time = parse_time(slot.value["value"], config.locale)
                new_request.set_time(time, str_time)
                used_slots.append(slot)

            if slot.slot_name == slot_names["location"]:
                new_request.location = parse_location(slot.value["value"], config.locale)
                used_slots.append(slot)

    for slot in used_slots:
        slots.remove(slot)

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
