from enum import Enum

from rhasspy_weather.data_types.weather_type import WeatherType


class TemperatureType(WeatherType, Enum):
    COLD = "cold"
    WARM = "warm"
