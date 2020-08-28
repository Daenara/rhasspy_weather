from enum import Enum

from rhasspy_weather.data_types.config import get_config


class WeatherCondition:
    def __init__(self, severity, description, condition_type):
        self.severity = severity
        self.description = description
        if description is "":
            try:
                self.description = get_config().locale.conditions[condition_type][severity]
            except KeyError:
                pass
        self.condition_type = condition_type

    def __eq__(self, other):
        return self.description == other.description

    def __str__(self):
        return "[" + str(self.condition_type) + ", " + str(self.severity) + ", " + str(self.description) + "]"

    def __repr__(self):
        return "[" + str(self.condition_type) + ", " + str(self.severity) + ", " + str(self.description) + "]"


class ConditionType(Enum):
    RAIN = "rain"
    SNOW = "snow"
    CLOUDS = "clouds"
    MIST = "mist"
    THUNDERSTORM = "thunderstorm"
    CLEAR = "clear"
    WIND = "wind"
    SUN = "sun"  # clear during daytime
    STARS = "stars"  # clear during night
    GENERAL = "general"
    UNKNOWN = "unknown"
