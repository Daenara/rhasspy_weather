import datetime
from typing import TypeVar

from rhasspy_weather.data_types.condition import ConditionType
from rhasspy_weather.data_types.error import WeatherError, ErrorCode
from rhasspy_weather.data_types.location import Location
from rhasspy_weather.utils import dt_utils
import logging

log = logging.getLogger(__name__)

InputTime = TypeVar("InputTime", str, int)


def parse_date(date: str, locale):
    log.debug(f"parse date - {date}")

    named_days_lowercase = [x.lower() for x in locale.named_days.keys()]
    named_days_synonyms_lowercase = [x.lower() for x in locale.named_days_synonyms.keys()]
    # is it a named day (tomorrow, etc.)?
    if date.lower() in named_days_lowercase + named_days_synonyms_lowercase:
        log.debug("date is specified by name")
        return dt_utils.named_day_to_date(date), dt_utils.named_day_to_str(date)

    # is a weekday named?
    weekdays_lowercase = [x.lower() for x in locale.weekday_names]
    if date.lower() in weekdays_lowercase:
        log.debug("date is specified by weekday name")
        new_date = dt_utils.weekday_to_date(date.lower())
        return new_date, weekdays_lowercase[new_date.weekday()]

    # was a date specified (specified by rhasspy as "daynumber monthname")?
    if ' ' in date:
        log.debug("date was specified in form 'day month'")
        return dt_utils.date_string_to_date(date), dt_utils.date_string_to_str(date)

    log.error("Unknown date format")
    raise WeatherError(ErrorCode.DATE_ERROR)


def parse_time(time: InputTime, locale):
    log.debug(f"parse time - {time}")
    if time != "":
        log.debug("intent contains a specified time")

        if isinstance(time, str):
            named_times_lowercase = [x.lower() for x in locale.named_times.keys()]
            named_times_synonyms_lowercase = [x.lower() for x in locale.named_times_synonyms.keys()]

            # was something like midday specified (listed in locale.named_times or in locale.named_times_synonyms)?
            if time.lower() in named_times_lowercase + named_times_synonyms_lowercase:
                log.debug("time is specified by name")
                return dt_utils.named_time_to_time(time), dt_utils.named_day_to_str(time)

            # was it hours and minutes (specified as "HH MM" by rhasspy intent)?
            if ' ' in time:
                log.debug("time was specified in form 'HH MM'")
                time = datetime.datetime.strptime(time, '%H %M').time()
                return time, locale.format_userdefined_time(time.hour, time.minute)

            log.error("Unknown format for time string")
            raise WeatherError(ErrorCode.TIME_ERROR)
        # is it only an hour (no way to only specify minutes, if it is an int, it is hours)?
        elif isinstance(time, int):
            log.debug("time specified was hours (as a number)")
            time = datetime.time(time, 0)
            return time, locale.format_userdefined_time(time.hour)
        else:
            log.error("Unknown time format")
            raise WeatherError(ErrorCode.TIME_ERROR)


def parse_location(location: str, locale):
    log.debug(f"parse location - {location}")
    return Location(location)


def parse_condition(condition: str, locale):
    log.debug(f"parse condition - {condition}")
    condition = condition.lower()
    if condition in locale.condition_types:
        return locale.condition_types[condition]
    elif condition in locale.condition_synonyms:
        return locale.condition_types[locale.condition_synonyms[condition]]
    else:
        return ConditionType.UNKNOWN


def parse_item(item: str, locale):
    log.debug(f"parse item - {item}")
    items = locale.rain_items + locale.cold_items + locale.warm_items + locale.sun_items
    items_lowercase = [x.lower() for x in items]
    if item.lower() in items_lowercase:
        return items[items_lowercase.index(item.lower())]


def parse_temperature(temperature: str, locale):
    log.debug(f"parse temperature - {temperature}")
    if temperature in locale.temperature_types:
        return locale.temperature_types[temperature]
    elif temperature in locale.temperature_synonyms:
        return locale.temperature_types[locale.temperature_synonyms[temperature]]
