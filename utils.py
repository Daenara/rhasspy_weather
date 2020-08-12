import datetime
import logging
import math

from dateutil.relativedelta import relativedelta
from .data_types.config import get_config

log = logging.getLogger(__name__)


def get_date_with_year(day, month, can_be_past_date=False):
    """
    Args:
        day: number of day - int
        month: number of month - int
        can_be_past_date: True if dates before today should be in the past, else False (default)

    Takes a day and a month without a year and outputs a datetime.date with the year. The year is
    the current year unless the date has already passed, then the boolean switch decides. If that is True
    the year will be the same year, if it is False then it might return the next.

    Wrong dates (like the 31.06.) will not throw an error but instead give a valid day the next month based
    on the number of days it differs from today (so the 31.02. turns into 01.07).
    """
    today = datetime.datetime.now(get_config().timezone).date()
    delta_days = day - today.day
    delta_month = month - today.month
    delta_year = 0
    if not can_be_past_date:
        if delta_month < 0:
            delta_year = 1
    then = today + relativedelta(years=delta_year, months=delta_month, days=delta_days)
    return then


def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)


def format_string(input_string):
    input_string = input_string.replace("..", ".")
    input_string = input_string.replace(" .", ".")
    input_string = input_string.replace("   ", " ")
    input_string = input_string.replace("  ", " ")
    input_string = input_string.replace(" :", ":")
    input_string = input_string[0].capitalize() + input_string[1:]
    return input_string