import datetime
import logging

from rhasspy_weather.utils import dt_utils as dt_utils
from rhasspy_weather.data_types.condition import ConditionType
from rhasspy_weather.data_types.error import WeatherError, ErrorCode
from rhasspy_weather.data_types.location import Location
from rhasspy_weather.data_types.request import WeatherRequest, DateType, ForecastType, Grain
from rhasspy_weather.data_types.config import get_config

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

    # if a day was specified
    log.debug("parse_date")
    if slot_names["day"] in slots and slots[slot_names["day"]] != "":
        new_request.request_date, new_request.date_specified = parse_date(slots, config.locale)

    # if a time was specified
    log.debug("parse_time")
    if slot_names["time"] in slots and slots[slot_names["time"]] != "":
        time, str_time = parse_time(slots, config.locale)
        if isinstance(time, tuple):
            new_request.date_type = DateType.INTERVAL
            new_request.start_time, new_request.end_time = time
        new_request.time_specified = str_time
        new_request.grain = Grain.HOUR

    # location
    log.debug("parse_location")
    if slot_names["location"] in slots and slots[slot_names["location"]] != "":
        log.debug("a location was specified")
        new_request.location = Location(slots[slot_names["location"]])

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
        if slots[slot_names["condition"]] in locale.condition_types:
            new_request.requested = locale.condition_types[slots[slot_names["condition"]]]
        elif slots[slot_names["condition"]] in locale.condition_synonyms:
            new_request.requested = locale.condition_types[locale.condition_synonyms[slots[slot_names["condition"]]]]
        else:
            new_request.requested = ConditionType.UNKNOWN
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
        items = locale.rain_items + locale.cold_items + locale.warm_items + locale.sun_items
        items_lowercase = [x.lower() for x in items]
        if slots[slot_names["item"]].lower() in items_lowercase:
            new_request.requested = items[items_lowercase.index(slots[slot_names["item"]].lower())]
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
        if slots[slot_names["temperature"]] in locale.temperature_types:
            new_request.requested = locale.temperature_types[slots[slot_names["temperature"]]]
        elif slots[slot_names["temperature"]] in locale.temperature_synonyms:
            new_request.requested = locale.temperature_types[locale.temperature_synonyms[slots[slot_names["temperature"]]]]
    return new_request


def parse_date(slots, locale):
    log.debug("intent contains a specified day")

    named_days_lowercase = [x.lower() for x in locale.named_days.keys()]
    named_days_synonyms_lowercase = [x.lower() for x in locale.named_days_synonyms.keys()]
    # is it a named day (tomorrow, etc.)?
    if slots[slot_names["day"]].lower() in named_days_lowercase + named_days_synonyms_lowercase:
        log.debug("date is specified by name")
        return dt_utils.named_day_to_date(slots[slot_names["day"]]), dt_utils.named_day_to_str(slots[slot_names["day"]])

    # is a weekday named?
    weekdays_lowercase = [x.lower() for x in locale.weekday_names]
    if slots[slot_names["day"]].lower() in weekdays_lowercase:
        log.debug("date is specified by weekday name")
        new_date = dt_utils.weekday_to_date(slots[slot_names["day"]].lower())
        return new_date, weekdays_lowercase[new_date.weekday()]

    # was a date specified (specified by rhasspy as "daynumber monthname")?
    if ' ' in slots[slot_names["day"]]:
        log.debug("date was specified in form 'day month'")
        return dt_utils.date_string_to_date(slots[slot_names["day"]]), dt_utils.date_string_to_str(slots[slot_names["day"]])

    log.error("Unknown date format")
    raise WeatherError(ErrorCode.DATE_ERROR)


def parse_time(slots, locale):
    if slot_names["time"] in slots and slots[slot_names["time"]] != "":
        log.debug("intent contains a specified time")

        if isinstance(slots[slot_names["time"]], str):
            named_times_lowercase = [x.lower() for x in locale.named_times.keys()]
            named_times_synonyms_lowercase = [x.lower() for x in locale.named_times_synonyms.keys()]

            # was something like midday specified (listed in locale.named_times or in locale.named_times_synonyms)?
            if slots[slot_names["time"]].lower() in named_times_lowercase + named_times_synonyms_lowercase:
                log.debug("time is specified by name")
                return dt_utils.named_time_to_date(slots[slot_names["time"]]), dt_utils.named_day_to_str(slots[slot_names["time"]])

            # was it hours and minutes (specified as "HH MM" by rhasspy intent)?
            if ' ' in slots[slot_names["time"]]:
                log.debug("time was specified in form 'HH MM'")
                time = datetime.datetime.strptime(slots[slot_names["time"]], '%H %M').time()
                return time, locale.format_userdefined_time(time.hour, time.minute)

            log.error("Unknown format for time string")
            raise WeatherError(ErrorCode.TIME_ERROR)
        # is it only an hour (no way to only specify minutes, if it is an int, it is hours)?
        elif isinstance(slots[slot_names["time"]], int):
            log.debug("time specified was hours (as a number)")
            time = datetime.time(slots[slot_names["time"]], 0)
            return time, locale.format_userdefined_time(time.hour)
        else:
            log.error("Unknown time format")
            raise WeatherError(ErrorCode.TIME_ERROR)
