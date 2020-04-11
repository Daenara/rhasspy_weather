from rhasspy_weather.data_types.item import WeatherItem


class WeatherItemList:

    def __init__(self):
        self.__items = []

    def __len__(self):
        return len(self.__items)

    def __iter__(self):
        for item in self.__items:
            yield item

    def __str__(self):
        return str(self.__items)

    __repr__ = __str__

    def add_item(self, name, prefix, suffix, condition_list):
        item = WeatherItem(name, prefix, suffix, condition_list)
        if item not in self.__items:
            self.__items.append(item)

    def get_items_for_condition(self, condition):
        output = []
        for item in self.__items:
            if item.is_for_condition_type(condition):
                output.append(item)
        return output

    def get_item_names_for_condition(self, condition):
        output = []
        for item in self.__items:
            if item.is_for_condition_type(condition):
                output.append(item.name)
        return output

    def is_in_list(self, item_name):
        item = WeatherItem(item_name)
        return item in self.__items

    def get_item(self, item_name):
        if self.is_in_list(item_name):
            item = WeatherItem(item_name)
            return self.__items[self.__items.index(item)]
