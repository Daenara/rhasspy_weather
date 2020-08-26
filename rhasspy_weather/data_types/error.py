import logging
import random
from enum import Enum

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
    MQTT_CONNECTION_ERROR = "mqtt_error"


class Error(Exception):
    pass


class WeatherError(Error):
    def __init__(self, error_code: ErrorCode, description: str = ""):
        from rhasspy_weather.data_types.config import get_config
        locale = get_config().locale
        self.description = description
        self.error_code = error_code
        self.message = random.choice(locale.status_response[error_code])
        log.error(description)


class ConfigError(Error):
    def __init__(self, message: str, description: str = "", error_code=None):
        self.message = message
        self.description = description
        if type(error_code) == ErrorCode:
            from rhasspy_weather.data_types.config import get_config
            locale = get_config().locale
            self.message = random.choice(locale.status_response[error_code])
