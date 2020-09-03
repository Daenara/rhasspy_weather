import datetime
from typing import Tuple

from rhasspy_weather.data_types.weather_at_time import WeatherAtTime


class Weather:
    def __init__(self):
        self.__weather = {}

    def add_weather(self, date: datetime.date, weather_at_time: WeatherAtTime):
        self.__weather[date] = self.__weather.get(date, [])
        self.__weather[date].append(weather_at_time)

    def get_weather_for_date(self, date: datetime.date):
        return self.__weather.get(date, [])

    def get_weather_at_time(self, date: datetime.date, time: datetime.time):
        return self.get_weather_at_interval(date, (time, time))

    def get_weather_at_interval(self, date: datetime.date, interval: Tuple[datetime.time, datetime.time]):
        output = []
        for weather_at_time in self.__weather.get(date, []):
            if interval[0] <= weather_at_time.time < interval[1] or weather_at_time.time <= interval[1] <= weather_at_time.end_time:
                output.append(weather_at_time)
        return output
