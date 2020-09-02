import datetime
from typing import Tuple

from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.error import WeatherError, ErrorCode
from rhasspy_weather.data_types.fixed_times import FixedTimes
from rhasspy_weather.data_types.request import DateType, Grain


class WeatherReport:
    def __init__(self, request, forecast):
        config = get_config()

        self.__weather = {}
        self.speech = ""

        if request.date_type == DateType.FIXED:
            if request.grain == Grain.DAY:
                if config.detail:
                    for fixed_time in [FixedTimes.MORNING, FixedTimes.AFTERNOON, FixedTimes.EVENING]:
                        self.set_weather(fixed_time.value, forecast.weather_for_interval(request.request_date, fixed_time.value[0], fixed_time.value[1]))
                else:
                    self.set_weather((datetime.time.min, datetime.time.max), forecast.weather_for_interval(datetime.time.min, datetime.time.max))
            elif request.grain == Grain.HOUR:
                self.set_weather((request.start_time, request.start_time), forecast.weather_for_interval(request.request_date, request.start_time, request.start_time))
        elif request.date_type == DateType.INTERVAL:
            self.set_weather((request.start_time, request.end_time), forecast.weather_for_interval(request.request_date, request.start_time, request.end_time))

        if self.__weather is {}:
            raise WeatherError(ErrorCode.NO_WEATHER_FOR_DAY_ERROR)

    @property
    def weather(self):
        return self.__weather

    def set_weather(self, key, value):
        if value is not None:
            self.__weather[key] = value
