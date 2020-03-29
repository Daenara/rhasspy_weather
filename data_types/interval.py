from rhasspy_weather.data_types.condition import ConditionType

import logging

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
        self.__rain = 0
        self.__thunderstorm = 0
        self.__mist = 0
        self.__snow = 0
        self.__clouds = 0
        self.__clear = 0
        self.__change_count = 0

    # puts information into itself
    def add_information(self, weather_at_time):
        self.__change_count = self.__change_count + 1
        if weather_at_time.temperature > self.max_temperature:
            self.max_temperature = weather_at_time.temperature
        if weather_at_time.temperature < self.min_temperature:
            self.min_temperature = weather_at_time.temperature
        if weather_at_time.weather_condition_obj not in self.weather_condition_list:
            self.weather_condition_list.append(weather_at_time.weather_condition_obj)
        self.__increase_counter(weather_at_time.weather_condition_obj.condition_type)

    # counts how many occurrences of a certain weather type there are
    def __increase_counter(self, condition_type):
        if condition_type == ConditionType.RAIN: 
            self.__rain = self.__rain + 1
        elif condition_type == ConditionType.THUNDERSTORM:
            self.__thunderstorm = self.__thunderstorm + 1
        elif condition_type == ConditionType.SNOW:
            self.__snow = self.__snow + 1
        elif condition_type == ConditionType.CLOUDS:
            self.__clouds = self.__clouds + 1
        elif condition_type == ConditionType.CLEAR:
            self.__clear = self.__clear + 1
        elif condition_type == ConditionType.MIST:
            self.__mist = self.__mist + 1

    @property
    def is_rain_chance(self):
        return self.__rain > 0

    @property
    def is_thunderstorm_chance(self):
        return self.__thunderstorm > 0

    @property
    def is_snow_chance(self):
        return self.__snow > 0

    @property
    def is_cloudy(self):
        return self.__clouds > 0

    @property
    def is_misty(self):
        return self.__mist > 0

    @property 
    def is_clear(self):
        return self.__clear > 0

    @property
    def contains_information(self):
        return self.__change_count > 0

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
            if clouds_and_clear_exclusive == True: 
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
    def __add_element_to_condition_list(self, element, condition_list):
        if len(condition_list) == 0:
            condition_list.append(element)
        else:
            if element.condition in [x.condition for x in condition_list]:
                for x in condition_list[:]:
                    if x.condition == element.condition:
                        if element.severity > x.severity:
                            condition_list.remove(x)
                            condition_list.append(element)
            else:
                condition_list.append(element)
        