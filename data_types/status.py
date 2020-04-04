import logging
import random
from enum import Enum

from .config import get_config

log = logging.getLogger(__name__)


class StatusCode(Enum):
    NORMAL = "normal"
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


class Status:
    def __init__(self, status_code=StatusCode.NORMAL):
        self.status_code = status_code
        self.__last_change = ""

    @property
    def status_code(self):
        return self.__status_code

    @status_code.setter
    def status_code(self, val):
        self.__status_code = val

    @property
    def is_error(self):
        if self.status_code == StatusCode.NORMAL:
            return False
        return True

    @property
    def last_change_message(self):
        return self.__last_change

    def set_status(self, val):
        self.status_code = val
        self.__log_status()

    def status_response(self):
        locale = get_config().locale

        if self.status_code in locale.status_response:
            response = random.choice(locale.status_response[self.status_code])
        else:
            response = random.choice(locale.status_response[StatusCode.GENERAL_ERROR])

        if self.is_error:
            log.error("Status: {0} - {1}".format(StatusCode(self.status_code), response))
        else:
            log.info("Status: {0} - {1}".format(StatusCode(self.status_code), response))
        return response

    def __log_status(self):
        import inspect

        current_frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(current_frame, 3)
        self.__last_change = '{0}.{1} set the status to {2}'.format(caller_frame[3][3], caller_frame[2][3], self.status_code)
        if self.is_error:
            log.error(self.__last_change)
        else:
            log.info(self.__last_change)
