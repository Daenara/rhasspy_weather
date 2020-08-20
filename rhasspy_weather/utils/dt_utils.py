import datetime
import logging
from typing import Union, Tuple

from dateutil.relativedelta import relativedelta

from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.error import WeatherError, ErrorCode

log = logging.getLogger(__name__)


def get_date_with_year(day: int, month: int, can_be_past_date: bool = False) -> datetime.date:
    """
    Takes a day and a month without a year and outputs a datetime.date with the year. The year is
    the current year unless the date has already passed, then the boolean switch decides. If that is True
    the year will be the same year, if it is False then it might return the next.

    Wrong dates (like the 31.06.) will not throw an error but instead give a valid day the next month based
    on the number of days it differs from today (so the 31.02. turns into 01.07).

    Args:
        day: number of day - int
        month: number of month - int
        can_be_past_date: True if dates before today should be in the past, else False (default)

    Returns: date as datetime.date
    """
    today = datetime.datetime.now(get_config().timezone).date()
    delta_days = day - today.day
    delta_month = month - today.month
    delta_year = 0
    if not can_be_past_date:
        if delta_month < 0 or delta_days < 0:
            delta_year = 1

    return today + relativedelta(years=delta_year, months=delta_month, days=delta_days)


def named_day_to_date(named_day: str) -> datetime.date:
    """
    Parses a string containing a named day to the date.

    Args:
        named_day: string containing a valid named day (locale.named_days and locale.named_days_synonyms)

    Returns: the date of the named_day
    """
    locale = get_config().locale
    named_days_lowercase = [x.lower() for x in locale.named_days]
    named_days_synonyms_lowercase = [x.lower() for x in locale.named_days_synonyms]
    if named_day.lower() in named_days_synonyms_lowercase:
        index = named_days_synonyms_lowercase.index(named_day.lower())
        name = list(locale.named_days_synonyms.keys())[index]
        value = locale.named_days[locale.named_days_synonyms[name]]
    else:
        index = named_days_lowercase.index(named_day.lower())
        value = list(locale.named_days.values())[index]
    if isinstance(value, datetime.date):
        return value
    elif isinstance(value, int):
        return datetime.date.today() + datetime.timedelta(value)
    else:
        log.error("Invalid datatype specified in locale.named_days or locale.named_days_synonyms")
        raise WeatherError(ErrorCode.DATE_ERROR)


def named_day_to_str(named_day: str) -> str:
    """
    Takes a valid named day and formats it for output.

    Args:
        named_day: string containing a valid named day (locale.named_days and locale.named_days_synonyms)

    Returns: named_day formatted for output
    """
    locale = get_config().locale
    named_days_lowercase = [x.lower() for x in locale.named_days]
    named_days_synonyms_lowercase = [x.lower() for x in locale.named_days_synonyms]
    if named_day.lower() in named_days_synonyms_lowercase:
        index = named_days_synonyms_lowercase.index(named_day.lower())
        return list(locale.named_days_synonyms.keys())[index]
    else:
        index = named_days_lowercase.index(named_day.lower())
        return list(locale.named_days.keys())[index]


def weekday_to_date(weekday: str, next_week: bool = False) -> datetime.date:
    """
    Takes a string containing a valid weekday (in weekday_names of locale) and returns the date based on today.

    next_week is False (default):
    If today is Wednesday and weekday is "Thursday" it will return the date of tomorrow.
    If today is Wednesday and weekday is "Wednesday" it will return the date of next Wednesday.
    If today is Wednesday and weekday is "Tuesday" it will return the date of next Tuesday.

    next_week is True:
    If today is Wednesday and weekday is "Thursday" it will return the date Thursday next week.
    If today is Wednesday and weekday is "Wednesday" it will return the date of next Wednesday.
    If today is Wednesday and weekday is "Tuesday" it will return the date of next Tuesday.

    Args:
        weekday: string containing the weekday to parse
        next_week: (optional) boolean controlling of a date of the next week will be enforced, default is False

    Returns: the date of the requested weekday

    """
    config = get_config()
    today = datetime.datetime.now(config.timezone).date()
    weekdays_lowercase = [x.lower() for x in config.locale.weekday_names]
    weekday_number = weekdays_lowercase.index(weekday.lower())
    offset = weekday_number - today.weekday()
    if next_week or today.weekday() >= weekday_number:
        offset = offset + 7
    return today + datetime.timedelta(offset)


def date_string_to_str(input_string: str, separator: str = " ") -> str:
    """
    Takes strings in format 'day[separator]month' and formats them for output depending on how day and month are specified.
    If the month is specified as a month name it will output 'day. month', if month is numeric it will output 'day.month'.
    If neither is the case it will just return the input string.

    This function does not check if the date is valid. If '01 13' is used as an input '01.13' will be returned.

    Args:
        input_string: string to be formatted for output
        separator: an (optional) separator between day and month, default is ' '

    Returns: formatted output or the input string
    """
    locale = get_config().locale
    day, month = input_string.split(separator)
    months_lowercase = [x.lower() for x in locale.month_names]

    if month.lower() in months_lowercase:
        return day + ". " + locale.month_names[months_lowercase.index(month.lower())]
    elif month.isnumeric():
        return day + "." + month

    return input_string


def date_string_to_date(input_string: str, separator: str = " ") -> datetime.date:
    """
    Takes strings in format 'day[separator]month' and parses them as a date. If the input can't be parsed
    into a date a WeatherError occurs.

    Args:
        input_string: string to be parsed
        separator: an (optional) separator between day and month, default is ' '

    Returns: date in the form of datetime.date

    """
    locale = get_config().locale
    day, month = input_string.split(separator)
    months_lowercase = [x.lower() for x in locale.month_names]
    if month.lower() in months_lowercase:
        month_number = months_lowercase.index(month.lower()) + 1
    elif month.isnumeric():
        month_number = int(month)
    else:
        log.error("Unknown format for month")
        raise WeatherError(ErrorCode.DATE_ERROR)

    if not 1 <= month_number <= 12:
        log.error("There are exactly 12 months, but the specified date was outside of that")
        raise WeatherError(ErrorCode.DATE_ERROR)
    if day.isnumeric():
        day_number = int(day)
        if not 1 <= day_number <= 31:
            log.error("Days of the Month can only be between 1 and 31.")
            raise WeatherError(ErrorCode.DATE_ERROR)
    else:
        log.error("Unknown format for day")
        raise WeatherError(ErrorCode.DATE_ERROR)
    return get_date_with_year(day_number, month_number)


def named_time_to_date(named_time: str) -> Union[datetime.time, Tuple[datetime.time, datetime.time]]:
    """
    Parsed a string containing a named time into the time.

    Args:
        named_time: a valid named time(locale.named_times or locale.named_times_synonyms)

    Returns: either a time or a tuple containing start and end time of an interval
    """
    locale = get_config().locale
    named_times_lowercase = [x.lower() for x in locale.named_times.keys()]
    named_times_synonyms_lowercase = [x.lower() for x in locale.named_times_synonyms.keys()]
    if named_time.lower() in named_times_synonyms_lowercase:
        index = named_times_synonyms_lowercase.index(named_time.lower())
        name = list(locale.named_times_synonyms.keys())[index]
        value = locale.named_times[locale.named_times_synonyms[name]]
    else:
        index = named_times_lowercase.index(named_time.lower())
        value = list(locale.named_times.values())[index]
    if isinstance(value, datetime.time) or isinstance(value, tuple):
        return value
    else:
        log.error("Invalid time specified in locale.named_times or locale.named_times_synonyms")
        raise WeatherError(ErrorCode.TIME_ERROR)


def named_time_to_str(named_time: str) -> str:
    """
    Takes a named_time and formats it for output.
    Args:
        named_time: a valid named time(locale.named_times or locale.named_times_synonyms)

    Returns: the formatted string

    """
    locale = get_config().locale
    named_times_lowercase = [x.lower() for x in locale.named_times.keys()]
    named_times_synonyms_lowercase = [x.lower() for x in locale.named_times_synonyms.keys()]

    if named_time.lower() in named_times_synonyms_lowercase:
        index = named_times_synonyms_lowercase.index(named_time.lower())
        return list(locale.named_times_synonyms.keys())[index]
    else:
        index = named_times_lowercase.index(named_time.lower())
        return list(locale.named_times.keys())[index]
