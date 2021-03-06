import datetime
import logging
from enum import Enum

from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.error import ErrorCode, WeatherError
from rhasspy_weather.data_types.fixed_times import FixedTimes

log = logging.getLogger(__name__)


class WeatherRequest:
    """
    Class holding all the information that parse_intent_message found
    has many functions to return the information in 
    human- and machine readable ways
    Attributes:
    date_type : DateType
        Is the request for a fixed time or an interval
    grain : Grain
        How specific should the request be, days, hours
    request_date : datetime.date
        For when is the request
    location : Location
        Object containing location information
    requested : str
        Was a specific condition, item or temperature requested
    time_specified : str
        non parsed time for the request (used for output)
    date_specified : str
        non parsed date for the request (used for output)
    location_specified : bool
        True if the location was specified, False if default location is used (used for output)
    forecast_type : ForecastType
        Type of request, full, temperature, condition or item
    start_time : datetime.time
    end_time : datetime.time
    weekday : str
    string_date :str
    readable_date : str
    string_start_time : str
    readable_start_time : str
    string_end_time : str
    readable_end_time : str
    time_difference : int
    """

    def __init__(self, date_type, grain, request_date, forecast_type):
        """
        Parameters:
        date_type : DateType
        grain : Grain
        request_date : datetime.date
        forecast_type : ForecastType
        """

        config = get_config()

        self.__location = config.location
        self.date_type = date_type
        self.grain = grain
        self.request_date = request_date
        self.requested = ""
        self.start_time = None
        self.end_time = None
        self.time_specified = ""
        self.date_specified = ""
        self.location_specified = False
        self.forecast_type = forecast_type
        self.detail = config.detail
        self.__timezone = config.timezone
        self.__locale = config.locale
        self.times = []

        # weather apis don't have weather for the past, so no no need checking
        if self.request_date < datetime.datetime.now(self.__timezone).date():
            raise WeatherError(ErrorCode.PAST_WEATHER_ERROR)

    def __str__(self):
        return "(" + str(self.forecast_type) + ", " + str(self.date_type) + ", " + \
               str(self.grain) + ", " + self.string_date + ", " + str(self.start_time) + \
               ", " + str(self.end_time) + ", " + self.location.name + ", " + self.requested + ", " + str(self.detail) + ")"

    def __update_times(self):
        if self.detail and self.forecast_type is not ForecastType.ITEM:
            if not self.times:
                for fixed_time in [FixedTimes.MORNING, FixedTimes.AFTERNOON, FixedTimes.EVENING]:
                    self.times.append(fixed_time.value)
        else:
            if self.grain == Grain.HOUR:
                self.times = []
                self.times.append((self.start_time, self.end_time))
            elif self.grain == Grain.DAY:
                self.times = []
                self.times.append((datetime.time.min, datetime.time.max))

    def __get_valid_time(self, val):
        time = None

        if type(val) is datetime.time:
            time = val
        elif type(val) is str:
            try:
                time = datetime.datetime.strptime(val, "%H:%M:%S").time()
            except ValueError:
                raise WeatherError(ErrorCode.TIME_ERROR)
        if time is not None:
            # if the weather at midnight was requested change the day to the next day
            # I say the next day is after 11:59PM of the day requested)
            if self.grain == Grain.HOUR and time == datetime.time.min:
                self.request_date = self.request_date + datetime.timedelta(days=1)
            # if the request was for today and the time has already passed I assume it meant the time +12h (PM instead of AM)
            elif self.grain == Grain.HOUR and self.request_date == datetime.datetime.now(self.__timezone).date() and \
                    datetime.datetime.now(self.__timezone).time() > time and time < datetime.time(12, 0):
                return time.replace(hour=time.hour + 12)
            return time
        raise WeatherError(ErrorCode.TIME_ERROR)

    def set_time(self, time, str_time):
        self.grain = Grain.HOUR
        if isinstance(time, tuple):
            self.date_type = DateType.INTERVAL
            self.start_time = self.__get_valid_time(time[0])
            self.end_time = self.__get_valid_time(time[1])
        else:
            self.start_time = self.__get_valid_time(time)
        self.time_specified = str_time

        if self.request_date == datetime.datetime.now(self.__timezone).date() and self.start_time < datetime.datetime.now(self.__timezone).time():
            raise WeatherError(ErrorCode.PAST_WEATHER_ERROR)

        self.__update_times()

    @property
    def location(self):
        return self.__location

    @location.setter
    def location(self, val):
        self.__location = val
        self.location_specified = True

    @property
    def grain(self):
        return self.__grain

    @grain.setter
    def grain(self, val):
        if type(val) is Grain:
            self.__grain = val

    @property
    def date_type(self):
        return self.__date_type

    @date_type.setter
    def date_type(self, val):
        if type(val) is DateType:
            self.__date_type = val

    @property
    def forecast_type(self):
        return self.__forecast_type

    @forecast_type.setter
    def forecast_type(self, val):
        if type(val) is ForecastType:
            self.__forecast_type = val

    @property
    def request_date(self):
        return self.__request_date

    @request_date.setter
    def request_date(self, val):
        if type(val) is datetime.date:
            self.__request_date = val
        elif type(val) is str:
            self.__request_date = datetime.datetime.strptime(val, "%Y-%m-%d").date()
        else:
            raise WeatherError(ErrorCode.DATE_ERROR)

    @property
    def weekday(self):
        return self.__locale.weekday_names[self.request_date.weekday()]

    @property
    def readable_date(self):
        return self.request_date.strftime("%d. %B")

    @property
    def string_date(self):
        return self.request_date.strftime("%Y-%m-%d")

    @property
    def string_start_time(self):
        if self.start_time:
            return self.start_time.strftime("%H:%M:%S")
        return ""

    @property
    def string_end_time(self):
        if self.end_time:
            return self.end_time.strftime("%H:%M:%S")
        return ""

    @property
    def readable_start_time(self):
        if self.start_time:
            return self.start_time.strftime("%H:%M")
        return ""

    @property
    def readable_end_time(self):
        if self.end_time:
            return self.end_time.strftime("%H:%M")
        return ""

    @property
    def time_difference(self):
        time_difference = (self.request_date - datetime.datetime.now(self.__timezone).date()).days
        if self.grain == Grain.HOUR and self.start_time == datetime.time(0, 0, 0):
            return time_difference - 1
        return time_difference


# WeatherRequest for a fixed time or an interval?
class DateType(Enum):
    FIXED = "fixed"
    INTERVAL = "interval"


# What kind of WeatherRequest was made?
class ForecastType(Enum):
    FULL = "full"
    TEMPERATURE = "temperature"
    ITEM = "item"
    CONDITION = "condition"


# my implementation of hermes-pythons Grain since that is the only thing I need from that package
class Grain(Enum):
    YEAR = 0
    QUARTER = 1
    MONTH = 2
    WEEK = 3
    DAY = 4
    HOUR = 5
