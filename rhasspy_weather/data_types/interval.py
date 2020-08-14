import logging

from rhasspy_weather.data_types.condition import ConditionType

log = logging.getLogger(__name__)


# Class used by WeatherReport and WeatherForecast
# filled by WeatherForecast and used by WeatherReport
# to generate the answer to the request
class WeatherInterval:
    def __init__(self):
        self.min_temperature = 99
        self.max_temperature = 0
        self.weather_condition_list = []
        self.pressure = 0
        self.humidity = 0
        self.wind_speed = 0
        self.wind_direction = 0
        self.__change_count = 0
        self.__condition_counts = {}

    def __str__(self):
        return f"[count: {self.__change_count}, min_temp: {self.min_temperature}, max_temp: {self.max_temperature}, pressure: {self.pressure}, humidity: {self.humidity}]"

    # puts information into itself
    def add_information(self, weather_at_time):
        self.__change_count = self.__change_count + 1
        if weather_at_time.temperature > self.max_temperature:
            self.max_temperature = weather_at_time.temperature
        if weather_at_time.temperature < self.min_temperature:
            self.min_temperature = weather_at_time.temperature
        if weather_at_time.main_condition not in self.weather_condition_list:
            self.weather_condition_list.append(weather_at_time.main_condition)
        self.__increase_counter(weather_at_time.main_condition.condition_type)

    # counts how many occurrences of a certain weather type there are
    def __increase_counter(self, condition_type):
        if condition_type not in self.__condition_counts:
            self.__condition_counts[condition_type] = 0
        self.__condition_counts[condition_type] = self.__condition_counts[condition_type] + 1

    @property
    def contains_information(self):
        return self.__change_count > 0

    def is_weather_chance(self, condition_type):
        return self.__condition_counts.get(condition_type, 0) > 0

    # creates a list of condition descriptions to be used in output
    def get_output_condition_list(self, clouds_and_clear_exclusive=False):
        if len(self.weather_condition_list) == 0:
            log.error("Empty interval. There should be something here")
            return []
        elif len(self.weather_condition_list) == 1:
            return [self.weather_condition_list[0].description]

        selected = []
        for x in self.weather_condition_list:
            # clear sky and clouds in the same interval seems like it might be
            # something that could be mutual exclusive, at least if the interval
            # is short so there is an option to only add one of those (the one
            # that occurs more often, if both occur at the same frequency, clouds 
            # are added)
            if clouds_and_clear_exclusive:
                if x.condition_type == ConditionType.CLOUDS:
                    if self.__clouds >= self.__clear:
                        self.__add_element_to_condition_list(x, selected)
                if x.condition_type == ConditionType.CLEAR:
                    if self.__clear > self.__clouds:
                        self.__add_element_to_condition_list(x, selected)
            else:
                self.__add_element_to_condition_list(x, selected)

        conditions = []
        for x in selected:
            conditions.append(x.description)
        return conditions

    # makes sure that only one element of a condition type is in the list (the most severe one)
    @staticmethod
    def __add_element_to_condition_list(element, condition_list):
        if len(condition_list) == 0:
            condition_list.append(element)
        else:
            if element.condition_type in [x.condition_type for x in condition_list]:
                for x in condition_list[:]:
                    if x.condition_type == element.condition_type:
                        if element.severity > x.severity:
                            condition_list.remove(x)
                            condition_list.append(element)
            else:
                condition_list.append(element)
