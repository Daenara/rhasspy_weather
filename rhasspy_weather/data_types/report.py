import datetime
import math
import random
import sys
from typing import Tuple

from rhasspy_weather.data_types import item_list
from rhasspy_weather.data_types.condition import ConditionType, WeatherCondition
from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.error import WeatherError, ErrorCode
from rhasspy_weather.data_types.fixed_times import FixedTimes
from rhasspy_weather.data_types.request import DateType, Grain, ForecastType


class WeatherReport:
    def __init__(self, request, weather, interval: Tuple[datetime.time, datetime.time] = None):
        self.config = get_config()

        self.request = request

        self.__weather = []
        self.speech = ""
        self.min_temperature = math.inf
        self.max_temperature = -math.inf
        self.min_pressure = math.inf
        self.max_pressure = -math.inf
        self.min_humidity = math.inf
        self.max_humidity = -math.inf
        self.weather_condition_list = []
        self.__change_count = 0
        self.__condition_counts = {}

        if interval:
            self.interval = interval
        else:
            if request.date_type == DateType.FIXED:
                if request.grain == Grain.DAY:
                    self.interval = (datetime.time.min, datetime.time.max)
                elif request.grain == Grain.HOUR:
                    self.interval = (request.start_time, request.start_time)
                else:
                    raise WeatherError(ErrorCode.NOT_IMPLEMENTED_ERROR)
            elif request.date_type == DateType.INTERVAL:
                if request.grain == Grain.HOUR:
                    self.interval = (request.start_time, request.end_time)
                else:
                    raise WeatherError(ErrorCode.NOT_IMPLEMENTED_ERROR)

        self.__weather = self.__weather + weather.get_weather_at_interval(request.request_date, self.interval)

        if not self.__weather:
            raise WeatherError(ErrorCode.NO_WEATHER_FOR_DAY_ERROR)

        self.__apply_weather()

    def __str__(self):
        return f"[count: {self.__change_count}, min_temp: {self.min_temperature}, max_temp: {self.max_temperature}]"

    def report_item(self):
        requested_item = item_list.items.get_item(self.request.requested)
        true_conditions = []
        false_conditions = []
        for condition in self.weather_condition_list:
            if condition.condition_type in requested_item.weather_types:
                answer_type = "other"
                if not true_conditions:
                    answer_type = "main"

                true_conditions.append(random.choice(self.config.locale.answers_true[condition.condition_type][answer_type]))
            else:
                answer_type = "other"
                if not false_conditions:
                    answer_type = "main"

                false_conditions.append(random.choice(self.config.locale.answers_true[condition.condition_type][answer_type]))

        if true_conditions:
            print(true_conditions)
        else:
            prefix = random.choice(self.config.locale.general_answers["negative"]) + ", " + random.choice(self.config.locale.general_answers["item_not_needed"]).format(item=self.config.locale.format_item_for_output(requested_item.name))
            print(prefix)
            print(self.config.locale.combine_conditions(false_conditions))

    def __apply_weather(self):
        for weather_at_time in self.__weather:
            self.__change_count = self.__change_count + 1
            if weather_at_time.temperature > self.max_temperature:
                self.max_temperature = weather_at_time.temperature
            if weather_at_time.temperature < self.min_temperature:
                self.min_temperature = weather_at_time.temperature
            if weather_at_time.pressure > self.max_pressure:
                self.max_pressure = weather_at_time.pressure
            if weather_at_time.pressure < self.min_pressure:
                self.min_pressure = weather_at_time.pressure
            if weather_at_time.humidity > self.max_humidity:
                self.max_humidity = weather_at_time.humidity
            if weather_at_time.humidity < self.min_humidity:
                self.min_humidity = weather_at_time.humidity

            # TODO: maybe do something about the order
            for condition in [weather_at_time.main_condition] + weather_at_time.other_conditions:
                condition_type_list = [x.condition_type for x in self.weather_condition_list]
                if condition.condition_type not in condition_type_list:
                    self.weather_condition_list.append(condition)
                else:
                    condition_in_list = next(x for x in self.weather_condition_list if x.condition_type == condition.condition_type)
                    if condition.severity > condition_in_list.severity:
                        self.weather_condition_list.remove(condition_in_list)
                        self.weather_condition_list.append(condition)
                self.__increase_counter(condition.condition_type)

    # counts how many occurrences of a certain weather type there are
    def __increase_counter(self, condition_type):
        if condition_type not in self.__condition_counts:
            self.__condition_counts[condition_type] = 0
        self.__condition_counts[condition_type] = self.__condition_counts[condition_type] + 1

    def is_weather_chance(self, condition_type):
        return self.__condition_counts.get(condition_type, 0) > 0

    # creates a list of condition descriptions to be used in output
    def get_output_condition_list(self, clouds_and_clear_exclusive=False):
        if len(self.weather_condition_list) == 1:
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
                    if self.__condition_counts[ConditionType.CLOUDS] >= self.__condition_counts[ConditionType.CLEAR]:
                        self.__add_element_to_condition_list(x, selected)
                if x.condition_type == ConditionType.CLEAR:
                    if self.__condition_counts[ConditionType.CLEAR] > self.__condition_counts[ConditionType.CLOUDS]:
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



    @property
    def weather(self):
        return self.__weather

    def set_weather(self, key, value):
        if value is not None:
            self.__weather[key] = value
