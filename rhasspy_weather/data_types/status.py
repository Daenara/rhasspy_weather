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
        self.error_codes = []

    @property
    def status_code(self):
        return self.__status_code

    @status_code.setter
    def status_code(self, val):
        self.__status_code = val
        if val is not StatusCode.NORMAL and val not in self.error_codes:
            self.error_codes.append(val)

    @property
    def error_code_list(self):
        return self.error_codes

    @property
    def is_error(self):
        return len(self.error_codes) > 0

    @property
    def last_change_message(self):
        return self.__last_change

    def set_status(self, val):
        self.status_code = val
        self.__log_status()

    def status_response(self):
        response = self.get_error_message(self.__status_code)

        if self.is_error:
            log.error(f"Status: {StatusCode(self.status_code)} - {response}")
        else:
            log.info(f"Status: {StatusCode(self.status_code)} - {response}")
        return response

    def __log_status(self):
        import inspect

        current_frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(current_frame, 3)
        self.__last_change = 'f{caller_frame[3][3]}.{caller_frame[2][3]} set the status to {self.status_code}'
        if self.is_error:
            log.error(self.__last_change)
        else:
            log.info(self.__last_change)

    @staticmethod
    def get_error_message(status_code):
        locale = get_config().locale
        if status_code in locale.status_response:
            return random.choice(locale.status_response[status_code])
        return random.choice(locale.status_response[StatusCode.GENERAL_ERROR])
