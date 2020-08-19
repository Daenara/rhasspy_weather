import logging
import random
from enum import Enum

from .config import get_config

log = logging.getLogger(__name__)


class ErrorCode(Enum):
    NO_NETWORK_ERROR = "no_network_error"
    API_ERROR = "api_error"
    FUTURE_WEATHER_ERROR = "future_weather_error"
    NOT_IMPLEMENTED_ERROR = "not_implemented_error"
    LOCATION_ERROR = "location_error"
    PAST_WEATHER_ERROR = "past_weather_error"
    NO_WEATHER_FOR_DAY_ERROR = "no_weather_for_day_error"
    DATE_ERROR = "date_error"
    API_TIMEOUT_ERROR = "api_timeout_error"
    CONFIG_ERROR = "config_error"
    TIME_ERROR = "time_error"
    GENERAL_ERROR = "general_error"


class WeatherError(Exception):
    def __init__(self, message):
        locale = get_config().locale
        self.message = message
        if type(message) == ErrorCode:
            self.message = random.choice(locale.status_response[message])
        super().__init__(self.message)
