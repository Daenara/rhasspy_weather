from enum import Enum

from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.weather_type import WeatherType
from rhasspy_weather.utils.utils import normal_round


class ConditionType(WeatherType, Enum):
    RAIN = "rain"
    SNOW = "snow"
    CLOUDS = "clouds"
    MIST = "mist"
    THUNDERSTORM = "thunderstorm"
    CLEAR = "clear"
    WIND = "wind"
    SUN = "sun"  # clear during daytime
    STARS = "stars"  # clear during night


class WeatherCondition:
    def __init__(self, severity, description, condition_type: ConditionType):
        self.severity = severity
        self.description = description
        if description == "":
            try:
                self.description = get_config().locale.conditions[condition_type][severity]
            except KeyError:
                self.description = ""
        self.condition_type = condition_type

    def __eq__(self, other):
        return self.condition_type == other.condition_type and self.severity == other.severity

    def __str__(self):
        return "[" + str(self.condition_type) + ", " + str(self.severity) + ", " + str(self.description) + "]"

    def __repr__(self):
        return "[" + str(self.condition_type) + ", " + str(self.severity) + ", " + str(self.description) + "]"


class WindCondition(WeatherCondition):
    def __init__(self, wind_speed, wind_direction):
        config = get_config()
        if config.units == "imperial":
            wind_speed = wind_speed / 2.237
        severity = normal_round((wind_speed / 0.836) * (2 / 3))

        compass_index = int((wind_direction / 45) + 0.5) % 8
        compass_directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

        self.wind_speed = wind_speed
        self.wind_direction = compass_directions[compass_index]

        description = ""
        try:
            self.description = config.locale.conditions[ConditionType.WIND][severity]
        except KeyError:
            self.description = ""
        super().__init__(severity, description, ConditionType.WIND)

