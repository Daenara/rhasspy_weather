import datetime
import logging

from rhasspy_weather.data_types.request import WeatherRequest, DateType, ForecastType, Grain
from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.utils.parser import parse_date, parse_time, parse_condition, parse_temperature, parse_item, \
    parse_location

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


def parse_intent_message(intent_message: dict) -> WeatherRequest:
    """
    Parses any of the rhasspy weather intents.

    Args:
        intent_message: the rhasspy intent message

    Returns: WeatherRequest object

    """
    if "GetWeatherForecastCondition" == intent_message["intent"]["name"]:
        return parse_condition_intent(intent_message)
    elif "GetWeatherForecastItem" == intent_message["intent"]["name"]:
        return parse_item_intent(intent_message)
    elif "GetWeatherForecastTemperature" == intent_message["intent"]["name"]:
        return parse_temperature_intent(intent_message)

    return parse_general_intent(intent_message)


def parse_general_intent(intent_message: dict) -> WeatherRequest:
    """
    Parses general rhasspy weather intents.

    Args:
        intent_message: the rhasspy intent message

    Returns: WeatherRequest object

    """
    config = get_config()
    today = datetime.datetime.now(config.timezone).date()

    # define default request
    new_request = WeatherRequest(DateType.FIXED, Grain.DAY, today, ForecastType.FULL)

    slots = intent_message["slots"]

    if slot_names["day"] in slots and slots[slot_names["day"]] != "":
        new_request.request_date, new_request.date_specified = parse_date(slots[slot_names["day"]], config.locale)

    if slot_names["time"] in slots and slots[slot_names["time"]] != "":
        time, str_time = parse_time(slots[slot_names["time"]], config.locale)
        new_request.set_time(time, str_time)

    if slot_names["location"] in slots and slots[slot_names["location"]] != "":
        new_request.location = parse_location(slots[slot_names["location"]], config.locale)

    return new_request


def parse_condition_intent(intent_message: dict) -> WeatherRequest:
    """
    Parses rhasspy condition weather intent.

    Args:
        intent_message: the rhasspy intent message

    Returns: WeatherRequest object

    """
    locale = get_config().locale
    new_request = parse_general_intent(intent_message)

    slots = intent_message["slots"]
    new_request.forecast_type = ForecastType.CONDITION
    if slot_names["condition"] in slots:
        new_request.requested = parse_condition(slots[slot_names["condition"]], locale)
    return new_request


def parse_item_intent(intent_message: dict) -> WeatherRequest:
    """
    Parses rhasspy item weather intent

    Args:
        intent_message: the rhasspy intent message

    Returns: WeatherRequest object

    """
    locale = get_config().locale
    new_request = parse_general_intent(intent_message)

    slots = intent_message["slots"]
    new_request.forecast_type = ForecastType.ITEM
    if slot_names["item"] in slots:
        new_request.requested = parse_item(slots[slot_names["item"]], locale)
    return new_request


def parse_temperature_intent(intent_message: dict) -> WeatherRequest:
    """
    Parses rhasspy temperature weather intent

    Args:
        intent_message: the rhasspy intent message

    Returns: WeatherRequest object

    """
    locale = get_config().locale
    new_request = parse_general_intent(intent_message)

    slots = intent_message["slots"]
    new_request.forecast_type = ForecastType.TEMPERATURE
    if slot_names["temperature"] in slots:
        new_request.requested = parse_temperature(slots[slot_names["temperature"]], locale)
    return new_request
