from enum import Enum
from typing import List

from rhasspy_weather.data_types.weather_type import WeatherType
from rhasspy_weather.utils import utils


class NounType(Enum):
    SINGULAR = "singular"
    PLURAL = "plural"


class WeatherItem:
    def __init__(self, name: str, noun_type: NounType = NounType.SINGULAR, article: str = "", weather_type_list: List[WeatherType] = None):
        if weather_type_list is None:
            weather_type_list = []
        self.name = name
        self.noun_type = noun_type
        self.article = article
        self.weather_types = weather_type_list

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "{%s, %s, %s, %s}" % (self.name, self.noun_type, self.article, self.weather_types)

    __repr__ = __str__

    def is_for_weather_type(self, weather_type: WeatherType):
        return weather_type in self.weather_types

    def format_for_output(self, sentence="{article} {noun} {verb}"):
        from rhasspy_weather.data_types.config import get_config
        locale = get_config().locale

        return utils.remove_excessive_whitespaces(sentence.format(article=self.article, noun=self.name, verb=locale.grammar[self.noun_type]))
