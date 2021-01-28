import datetime
import json
import logging

from rhasspy_weather.data_types.request import WeatherRequest, DateType, ForecastType, Grain
from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.utils.parser import parse_date, parse_time, parse_condition, parse_item, parse_temperature, parse_location

log = logging.getLogger(__name__)


def parse_intent_message(args: json) -> WeatherRequest:
    """
    Parses any of the rhasspy weather intents.

    Args:
        args: dict containing the arguments

    Returns: WeatherRequest object

    """
    if hasattr(args, "condition") and args.condition is not None:
        return parse_condition_intent(args)
    elif hasattr(args, "item") and args.item is not None:
        return parse_item_intent(args)
    elif hasattr(args, "temperature") and args.temperature is not None:
        return parse_temperature_intent(args)

    return parse_general_intent(args)


def parse_general_intent(args: json) -> WeatherRequest:
    """
    Parses general rhasspy weather intents.

    Args:
        args: the rhasspy intent message

    Returns: WeatherRequest object

    """
    config = get_config()
    today = datetime.datetime.now(config.timezone).date()

    # define default request
    new_request = WeatherRequest(DateType.FIXED, Grain.DAY, today, ForecastType.FULL)

    if hasattr(args, "day") and args.day is not None:
        new_request.request_date, new_request.date_specified = parse_date(args.day, config.locale)

    if hasattr(args, "time") and args.time is not None:
        time, str_time = parse_time(args.time, config.locale)
        new_request.set_time(time, str_time)

    if hasattr(args, "location") and args.location is not None:
        new_request.location = parse_location(args.location, config.locale)

    return new_request


def parse_condition_intent(args: json) -> WeatherRequest:
    """
    Parses rhasspy condition weather intent.

    Args:
        args: the rhasspy intent message

    Returns: WeatherRequest object

    """
    locale = get_config().locale
    new_request = parse_general_intent(args)

    new_request.forecast_type = ForecastType.CONDITION
    arg_condition = args.condition
    if arg_condition is not None:
        new_request.requested = parse_condition(arg_condition, locale)
    return new_request


def parse_item_intent(args: json) -> WeatherRequest:
    """
    Parses rhasspy item weather intent

    Args:
        args: the rhasspy intent message

    Returns: WeatherRequest object

    """
    locale = get_config().locale
    new_request = parse_general_intent(args)

    new_request.forecast_type = ForecastType.ITEM
    arg_item = args.item
    if arg_item is not None:
        new_request.requested = parse_item(arg_item, locale)
    return new_request


def parse_temperature_intent(args: json) -> WeatherRequest:
    """
    Parses rhasspy temperature weather intent

    Args:
        args: the rhasspy intent message

    Returns: WeatherRequest object

    """
    locale = get_config().locale
    new_request = parse_general_intent(args)

    new_request.forecast_type = ForecastType.TEMPERATURE
    arg_temperature = args.temperature
    if arg_temperature is not None:
        new_request.requested = parse_temperature(arg_temperature, locale)
    return new_request


__template_values = None


def get_template_values(intent_message) -> dict:
    global __template_values
    if __template_values is None:
        __template_values = {}
        for key, value in vars(intent_message).items():
            __template_values["intent_" + key] = value
    return __template_values
