import datetime
import math
import random
from typing import Tuple, List

from rhasspy_weather.data_types import item_list
from rhasspy_weather.data_types.condition import ConditionType
from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.error import WeatherError, ErrorCode
from rhasspy_weather.data_types.request import DateType, Grain, ForecastType, WeatherRequest
from rhasspy_weather.data_types.temperature import TemperatureType
from rhasspy_weather.data_types.weather import Weather
from rhasspy_weather.utils import utils


class WeatherReport:
    """
    Class containing information about the weather for a specific WeatherRequest, as well as the answers formulated for TTS.
    """
    def __init__(self, request: WeatherRequest, weather_information: Weather, interval: Tuple[datetime.time, datetime.time] = None):
        if not (request.grain == Grain.DAY or request.grain == Grain.HOUR):
            raise WeatherError(ErrorCode.NOT_IMPLEMENTED_ERROR)

        self.config = get_config()

        self.request = request

        self.__weather = []
        self.speech = {}
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

        self.__weather = self.__weather + weather_information.get_weather_at_interval(request.request_date, self.interval)

        if not self.__weather:
            raise WeatherError(ErrorCode.NO_WEATHER_FOR_DAY_ERROR)

        self.__apply_weather()
        self.report()

    def __str__(self):
        return f"[count: {self.__change_count}, min_temp: {self.min_temperature}, max_temp: {self.max_temperature}]"

    def report(self):
        """Method that turns the weather information into text according to the WeatherRequest"""
        if self.request.forecast_type == ForecastType.TEMPERATURE:
            self.report_temperature()
        elif self.request.forecast_type == ForecastType.CONDITION:
            self.report_condition()
        elif self.request.forecast_type == ForecastType.FULL:
            self.report_temperature()
            self.report_condition()
            self.report_full()
        elif self.request.forecast_type == ForecastType.ITEM:
            self.report_item()

        self.speech[self.request.forecast_type] = self.format_when_and_where(self.speech[self.request.forecast_type], self.get_output_date_and_time(), self.get_output_location())

    def report_temperature(self):
        """Method that turns temperature information into text"""
        general_answer = random.choice(self.config.locale.temperature_answers[TemperatureType.GENERAL])
        if self.request.forecast_type == ForecastType.TEMPERATURE and type(self.request.requested) == TemperatureType:
            temperature_type = self.request.requested
            response_type = "false"
            if temperature_type == TemperatureType.COLD:
                if self.min_temperature <= self.config.temperature_cold_to:
                    response_type = "true"
            elif temperature_type == TemperatureType.WARM:
                if self.min_temperature >= self.config.temperature_warm_from:
                    response_type = "true"
            self.speech[ForecastType.TEMPERATURE] = random.choice(self.config.locale.temperature_answers[temperature_type][response_type]) + " "
            general_answer = self.format_when_and_where(general_answer)
        else:
            self.speech[ForecastType.TEMPERATURE] = ""

        temperature_output = self.config.locale.format_temperature_output(self.min_temperature, self.max_temperature)
        temperature_answer = general_answer.format(temperature=temperature_output, when="{when}", where="{where}")
        self.speech[ForecastType.TEMPERATURE] = self.speech[ForecastType.TEMPERATURE] + temperature_answer

    def report_condition(self):
        """Method that turns condition information into text"""
        if self.request.forecast_type == ForecastType.CONDITION and type(self.request.requested) == ConditionType:
            condition_type = self.request.requested
            response_type = "false"
            additional_information = ""
            if condition_type in [x.condition_type for x in self.weather_condition_list]:
                response_type = "true"
                prefix = random.choice(self.config.locale.general_answers["affirmative"])
            else:
                prefix = random.choice(self.config.locale.general_answers["negative"])
                additional_information = " " + random.choice(self.config.locale.general_answers["weather"])
            self.speech[ForecastType.CONDITION] = prefix + ", " + random.choice(self.config.locale.condition_answers[condition_type][response_type]) + additional_information
        else:
            self.speech[ForecastType.CONDITION] = random.choice(self.config.locale.condition_answers[ConditionType.GENERAL])

        self.speech[ForecastType.CONDITION] = self.speech[ForecastType.CONDITION].format(weather=self.format_conditions(), when="{when}", where="{where}")

    def report_full(self):
        self.speech[ForecastType.FULL] = self.speech[ForecastType.CONDITION] + " " + self.format_when_and_where(self.speech[ForecastType.TEMPERATURE])
        self.speech[ForecastType.FULL] = self.speech[ForecastType.FULL].format(weather=self.format_conditions(), when="{when}", where="{where}")

    def report_item(self):
        """Method that turns item information into text"""
        requested_item = item_list.items.get_item(self.request.requested)
        true_conditions = []
        false_conditions = []
        for condition in self.weather_condition_list:
            if condition.condition_type in requested_item.weather_types:
                true_conditions.append(condition)
            else:
                false_conditions.append(condition)

        if true_conditions:
            self.speech[ForecastType.ITEM] = random.choice(self.config.locale.general_answers["affirmative"]) + ", " + requested_item.format_for_output(random.choice(self.config.locale.general_answers["item_needed"])) + ". "
        else:
            self.speech[ForecastType.ITEM] = random.choice(self.config.locale.general_answers["negative"]) + ", " + requested_item.format_for_output(random.choice(self.config.locale.general_answers["item_not_needed"])) + ". "

        self.speech[ForecastType.ITEM] = self.speech[ForecastType.ITEM] + random.choice(self.config.locale.general_answers["weather"])
        self.speech[ForecastType.ITEM] = self.speech[ForecastType.ITEM].format(weather=self.format_conditions(), when="{when}", where="{where}")

    @staticmethod
    def format_when_and_where(answer: str, when: str = "", where: str = "") -> str:
        """
        Method that replaces {when} and {where} in a string while leaving {temperature} and {weather} alone

        Args:
            answer: the string to replace in
            when: value to replace {when} with, default is an empty string
            where: value to replace {where} with, default is an empty string

        Returns:
            The formatted string

        """
        answer = answer.format(when=when, where=where, temperature="{temperature}", weather="{weather}")
        answer = utils.format_string(answer)
        return answer

    def format_conditions(self) -> str:
        """
        Formats conditions with combining words according to locale

        Returns:
            the formatted string

        """
        return self.config.locale.combine_conditions(self.get_output_condition_list())

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

    def __increase_counter(self, condition_type: ConditionType):
        """counts how many occurrences of a certain weather type there are"""
        if condition_type not in self.__condition_counts:
            self.__condition_counts[condition_type] = 0
        self.__condition_counts[condition_type] = self.__condition_counts[condition_type] + 1

    def is_weather_chance(self, condition_type: ConditionType) -> bool:
        """
        Checks if there is a chance of condition_type

        Args:
            condition_type: which condition to check for

        Returns:
            True if condition can occur, else False

        """
        return self.__condition_counts.get(condition_type, 0) > 0

    def get_output_condition_list(self, clouds_and_clear_exclusive: bool = False) -> List[str]:
        """
        Method that creates a list of condition descriptions to be used for output

        Args:
            clouds_and_clear_exclusive: setting this to True means that either clouds or clear sky will be included.
            clear sky and clouds in the same interval seems like it might be something that could be mutual exclusive,
            at least if the interval is short so there is an option to only add one of those (the one that occurs more
            often, if both occur at the same frequency, clouds are added)

        Returns:
            A list containing the descriptions of the weather conditions that apply

        """
        if len(self.weather_condition_list) == 1:
            return [self.weather_condition_list[0].description]

        selected = []
        for x in self.weather_condition_list:
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

    def get_output_date_and_time(self) -> str:
        """
        Method that formats date and time for output. Respects formatting coded into locale

        Returns:
            string containing the formatted date and time

        """
        if self.request.date_specified != "":
            date = self.request.date_specified
        else:
            date = self.config.locale.format_output_date(self.request)
        if self.request.time_specified != "":
            time = self.request.time_specified
        else:
            if self.request.grain == Grain.HOUR:
                time = self.config.locale.format_output_time(self.request)
            else:
                time = ""

        if self.request.grain == Grain.HOUR:
            return date + " " + time
        return date

    def get_output_location(self):
        return self.config.locale.format_output_location(self.request.location.name) if self.request.location_specified else ""

    @staticmethod
    def __add_element_to_condition_list(element, condition_list):
        """makes sure that only one element of a condition type is in the list (the most severe one)"""
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
