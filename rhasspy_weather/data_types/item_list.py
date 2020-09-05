from typing import List

from rhasspy_weather.data_types.item import WeatherItem, NounType
from rhasspy_weather.data_types.weather_type import WeatherType

items = None


class WeatherItemList:

    def __init__(self):
        self.__items = []
        global items
        items = self

    def __len__(self):
        return len(self.__items)

    def __iter__(self):
        for item in self.__items:
            yield item

    def __str__(self):
        return str(self.__items)

    __repr__ = __str__

    def add_item(self, name: str, noun_type: NounType, weather_list: List[WeatherType], article: str = ""):
        item = WeatherItem(name, noun_type, article, weather_list)
        if item not in self.__items:
            self.__items.append(item)

    def get_items_for_weather(self, weather_type: WeatherType):
        output = []
        for item in self.__items:
            if item.is_for_weather_type(weather_type):
                output.append(item)
        return output

    def get_item_names_for_weather(self, weather_type: WeatherType):
        output = []
        for item in self.__items:
            if item.is_for_weather_type(weather_type):
                output.append(item.name)
        return output

    def is_in_list(self, item_name: str):
        item = WeatherItem(item_name)
        return item in self.__items

    def get_item(self, item_name: str):
        if self.is_in_list(item_name):
            item = WeatherItem(item_name)
            return self.__items[self.__items.index(item)]

    def get_all_item_names(self):
        return [i.name for i in self.__items]
