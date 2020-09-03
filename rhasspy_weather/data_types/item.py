from typing import List

from rhasspy_weather.data_types.weather_type import WeatherType


class WeatherItem:

    def __init__(self, name: str, prefix: str = "", suffix: str = "", weather_type_list: List[WeatherType] = None):
        if weather_type_list is None:
            weather_type_list = []
        self.__name = name
        self.__prefix = prefix
        self.__suffix = suffix
        self.__weather_list = weather_type_list

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__name == other.name
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "{%s, %s, %s, %s}" % (self.__name, self.__prefix, self.__suffix, self.__weather_list)

    __repr__ = __str__

    @property
    def name(self):
        return self.__name

    @property
    def weather_types(self):
        return self.__weather_list

    def is_for_weather_type(self, weather_type: WeatherType):
        return weather_type in self.__weather_list

    def format_for_output(self):
        output = self.__name
        if self.__prefix != "":
            output = self.__prefix + " " + output
        if self.__suffix != "":
            output = output + " " + self.__suffix
        return output
