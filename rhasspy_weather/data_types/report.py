import datetime
import logging
import random

from .config import get_config
from .fixed_times import FixedTimes
from .request import DateType, ForecastType, Grain
from .status import StatusCode, WeatherError
from .condition import ConditionType
from .temperature import TemperatureType
from ..utils import format_string

log = logging.getLogger(__name__)


class WeatherReport:
    """
    A class that generates a weather report out of a WeatherRequest and a WeatherForecast object.

    Attributes:
    request : WeatherRequest
        the request to be answered
    forecast : WeatherForecast
        the weather data that should be used in the answer

    Methods:
    generate_report()
        generates and returns the answer to the WeatherRequest as string
    """

    def __init__(self, request, forecast):
        """
        Parameters:
        request : WeatherRequest
            the request to be answered
        forecast : WeatherForecast
            the weather data that should be used in the answer
        """
        log.debug("weather report initialized")

        self.__config = get_config()

        self.__forecast = forecast
        self.__request = request
        self.__timezone = self.__config.timezone
        self.__locale = self.__config.locale

    def generate_report(self):
        """
        generates and returns the answer to the WeatherRequest as string
        If an error occurs it will return the error message as a string instead
        """
        log.debug(f"generating weather report")

        response = ""

        if not self.__forecast.has_weather_for_date(self.__request.request_date):
            log.debug("No weather for today")
            if self.__request.request_date == datetime.datetime.now(self.__timezone).date():
                if self.__request.date_type == DateType.FIXED:
                    log.debug("only weather for one day was requested, we don't have weather for that day so return with error message")
                    raise WeatherError(StatusCode.NO_WEATHER_FOR_DAY_ERROR)  # Error: day nearly over, no forecast in api response
                # overnight request and no weather for the other day, also
                elif self.__request.request_date == DateType.INTERVAL and self.__request.grain == Grain.HOUR \
                        and self.__request.end_time < self.__request.start_time \
                        and not self.__forecast.has_weather_for_date(self.__request.request_date + datetime.timedelta(days=1)):
                    raise WeatherError(StatusCode.NO_WEATHER_FOR_DAY_ERROR)  # Error: day nearly over, no forecast in api response
            else:
                raise WeatherError(StatusCode.FUTURE_WEATHER_ERROR)

        if not (self.__request.grain == Grain.DAY or self.__request.grain == Grain.HOUR):
            raise WeatherError(StatusCode.NOT_IMPLEMENTED_ERROR)

        if self.__request.forecast_type == ForecastType.TEMPERATURE:
            response = self.__generate_temperature_report()
        elif self.__request.forecast_type == ForecastType.CONDITION:
            response = self.__generate_condition_report()
        elif self.__request.forecast_type == ForecastType.FULL:
            response = self.__generate_full_report()
        elif self.__request.forecast_type == ForecastType.ITEM:
            response = self.__generate_item_report()

        log.debug(format_string(response))
        return format_string(response)

    # returns the answer to a question about the weather
    # called by generate_report()
    def __generate_full_report(self):
        log.debug(f"generating full report")
        response = ""
        if self.__request.date_type == DateType.FIXED:
            if self.__request.grain == Grain.DAY:
                response = self.__generate_full_report_day()
            elif self.__request.grain == Grain.HOUR:
                weather = self.__forecast.weather_at_time(self.__request.request_date, self.__request.start_time)
                response = self.__answer_condition(weather).format(when=self.__output_date_and_time, where=self.__output_location)
                response = response + " " + self.__answer_temperature(weather.min_temperature).format(when="", where="")
        elif self.__request.date_type == DateType.INTERVAL:
            weather = self.__forecast.weather_for_interval(self.__request.request_date, self.__request.start_time, self.__request.end_time)
            response = self.__answer_condition(weather).format(when=self.__output_date_and_time, where=self.__output_location)
            response = response + " " + self.__answer_temperature(weather.min_temperature, weather.max_temperature).format(when="", where="")
        return response

    # returns the answer to a question about the temperature
    # called by generate_report()
    def __generate_temperature_report(self):
        log.debug(f"generating temperature report")
        response = ""
        if self.__request.date_type == DateType.FIXED:
            if self.__request.grain == Grain.DAY:
                response = self.__generate_temperature_report_day()
            elif self.__request.grain == Grain.HOUR:
                weather = self.__forecast.weather_at_time(self.__request.request_date, self.__request.start_time)
                response = self.__answer_temperature(weather.min_temperature).format(when=self.__output_date_and_time, where=self.__output_location)
        elif self.__request.date_type == DateType.INTERVAL:
            weather = self.__forecast.weather_for_interval(self.__request.request_date, self.__request.start_time, self.__request.end_time)
            response = self.__answer_temperature(weather.min_temperature, weather.max_temperature).format(when=self.__output_date_and_time, where=self.__output_location)
        return response

    # returns a string answer to a question about the weather condition
    # called by generate_report()
    def __generate_condition_report(self):
        log.debug(f"generating condition report")
        response = ""
        if self.__request.date_type == DateType.FIXED:
            if self.__request.grain == Grain.DAY:
                response = self.__generate_condition_report_day()
            elif self.__request.grain == Grain.HOUR:
                weather_at_time = self.__forecast.weather_at_time(self.__request.request_date, self.__request.start_time)
                response = self.__answer_condition(weather_at_time).format(when=self.__output_date_and_time, where=self.__output_location)
        elif self.__request.date_type == DateType.INTERVAL:
            weather = self.__forecast.weather_for_interval(self.__request.request_date, self.__request.start_time, self.__request.end_time)
            response = self.__answer_condition(weather).format(when=self.__output_date_and_time, where=self.__output_location)
        return response

    # returns a string with the answer to the question about an item
    # called by generate_report()
    def __generate_item_report(self):
        log.debug(f"generating item report")

        item = self.__request.requested
        weather = None

        log.debug("Request: %s", str(self.__request))

        if self.__request.date_type == DateType.FIXED:
            if self.__request.grain == Grain.DAY:
                weather = self.__forecast.weather_for_day(self.__request.request_date)
            elif self.__request.grain == Grain.HOUR:
                weather = self.__forecast.weather_at_time(self.__request.request_date, self.__request.start_time)
        elif self.__request.date_type == DateType.INTERVAL:
            weather = self.__forecast.weather_for_interval(self.__request.request_date, self.__request.start_time, self.__request.end_time)

        if self.__request.requested in self.__locale.rain_items:
            if weather.is_weather_chance(ConditionType.RAIN):
                response_type = "rain"
            else:
                response_type = "no_rain"
        elif self.__request.requested in self.__locale.warm_items:
            if weather.max_temperature >= self.__config.temperature_warm_from:
                response_type = "warm"
            else:
                response_type = "not_warm"
        elif self.__request.requested in self.__locale.sun_items:
            day_weather = self.__forecast.weather_during_daytime(self.__request)
            if day_weather is not None:
                if day_weather.is_weather_chance(ConditionType.CLEAR):
                    if weather.max_temperature >= self.__config.temperature_warm_from:
                        response_type = "warm_and_sunny"
                    else:
                        response_type = "not_warm_and_sunny"
                else:
                    response_type = "not_sunny"
            else:
                response_type = "nighttime"
        elif self.__request.requested in self.__locale.cold_items:
            if weather.max_temperature < self.__config.temperature_cold_to:
                response_type = "cold"
            else:
                response_type = "not_cold"
        else:
            response_type = "unknown_item"
        return random.choice(self.__locale.item_answers[response_type]).format(when=self.__output_date_and_time, where=self.__output_location, item=self.__locale.format_item_for_output(item))

    # returns a string response with the weather forecast for a full day if detail=True in the config this answer may be rather long
    # called by __generate_full_report()
    def __generate_full_report_day(self):
        log.debug(f"generating full day report")
        if self.__request.detail:
            response = random.choice(self.__locale.condition_answers["general_weather_full"]).format(when=self.__output_date_and_time, where=self.__output_location)
            for fixed_time in [FixedTimes.MORNING, FixedTimes.AFTERNOON, FixedTimes.EVENING]:
                weather = self.__forecast.weather_for_interval(self.__request.request_date, fixed_time.value[0], fixed_time.value[1])
                if weather is not None:
                    response = response + self.__locale.fixed_times[fixed_time] + ": " + self.__locale.combine_conditions(weather.get_output_condition_list()) + ". "
                    response = response + self.__answer_temperature(weather.min_temperature, weather.max_temperature).format(when="", where="") + ". "
        else:
            weather_for_day = self.__forecast.weather_for_day(self.__request.request_date)
            response = self.__answer_condition(weather_for_day).format(when=self.__output_date_and_time, where=self.__output_location)
            response = response + " " + self.__answer_temperature(weather_for_day.min_temperature, weather_for_day.max_temperature).format(when="", where="")
        return response

    # returns a string response with the temperatures for a full day if detail=True in the config this answer may be rather long
    # called by __generate_temperature_report()
    def __generate_temperature_report_day(self):
        log.debug(f"generating temperature day report")
        if self.__request.detail and self.__request.requested is None:
            response = random.choice(self.__locale.temperature_answers["general_temperature_full"]).format(when=self.__output_date_and_time, where=self.__output_location)
            for fixed_time in [FixedTimes.MORNING, FixedTimes.AFTERNOON, FixedTimes.EVENING]:
                weather = self.__forecast.weather_for_interval(self.__request.request_date, fixed_time.value[0], fixed_time.value[1])
                if weather is not None:
                    response = response + self.__locale.fixed_times[fixed_time] + ": " + self.__locale.format_temperature_output(weather.min_temperature, weather.max_temperature) + ". "
        else:
            weather = self.__forecast.weather_for_day(self.__request.request_date)
            response = self.__answer_temperature(weather.min_temperature, weather.max_temperature).format(when=self.__output_date_and_time, where=self.__output_location)
        return response

    # returns a string response with the weather conditions for a full day if detail=True in the config this answer may be rather long
    # called by __generate_condition_report()
    def __generate_condition_report_day(self):
        log.debug(f"generating condition day report")
        if self.__request.detail:
            response = random.choice(self.__locale.condition_answers["general_weather_full"]).format(when=self.__output_date_and_time, where=self.__output_location)
            for fixed_time in [FixedTimes.MORNING, FixedTimes.AFTERNOON, FixedTimes.EVENING]:
                weather = self.__forecast.weather_for_interval(self.__request.request_date, fixed_time.value[0], fixed_time.value[1])
                if weather is not None:
                    response = response + self.__answer_condition(weather, False).format(when=self.__locale.fixed_times[fixed_time], where="") + ". "
        else:
            weather = self.__forecast.weather_for_day(self.__request.request_date)
            response = self.__answer_condition(weather, True).format(when=self.__output_date_and_time, where=self.__output_location)
        return response

    # returns a string with the temperature and placeholders for location and time
    def __answer_temperature(self, min_temp, max_temp=""):
        log.debug(f"generating response for temperature")

        if max_temp == "":
            max_temp = min_temp
        min_temp = int(min_temp)
        max_temp = int(max_temp)

        response_type = ""
        temperature_type = TemperatureType.GENERAL
        if self.__request.forecast_type == ForecastType.TEMPERATURE and type(self.__request.requested) == TemperatureType:
            temperature_type = self.__request.requested
            response_type = "false"
            if temperature_type == TemperatureType.COLD:
                if min_temp <= self.__config.temperature_cold_to:
                    response_type = "true"
            elif temperature_type == TemperatureType.WARM:
                if min_temp >= self.__config.temperature_warm_from:
                    response_type = "true"

        return random.choice(self.__locale.temperature_answers[temperature_type][response_type]).format(temperature=self.__locale.format_temperature_output(min_temp, max_temp), when="{when}", where="{where}")

    # returns a string with the weather condition and placeholders for location and time
    def __answer_condition(self, weather_obj, answer_question=True):
        log.debug(f"generating response for condition")
        response_type = ""
        condition_type = ConditionType.GENERAL
        prefix = ""
        suffix = ""
        output_conditions = self.__locale.combine_conditions(weather_obj.get_output_condition_list())
        if self.__request.forecast_type == ForecastType.CONDITION and type(self.__request.requested) == ConditionType:
            condition_type = self.__request.requested
            if self.__request.requested == ConditionType.SUN:
                if self.__request.start_time > self.__forecast.sunset:
                    # start time after sunset
                    if self.__request.end_time < self.__forecast.sunrise:
                        # end time before sunrise
                        response_type = "false"
                    else:
                        # end time after sunrise
                        # todo: figure out the difference between end_time and sunrise and only output sunny if it is the majority of time

                        day_weather = self.__forecast.weather_during_daytime(self.__request)
                        if day_weather is not None and day_weather.is_weather_chance(ConditionType.CLEAR):
                            response_type = "true"
                        else:
                            response_type = "false"
                else:
                    day_weather = self.__forecast.weather_during_daytime(self.__request)
                    if day_weather is not None and day_weather.is_weather_chance(ConditionType.CLEAR):
                        response_type = "true"
                    else:
                        response_type = "false"
            elif self.__request.requested == ConditionType.WIND:
                log.error("condition wind not implemented yet")
                self.status.set_status(StatusCode.NOT_IMPLEMENTED_ERROR)
                return self.status.status_response()
            else:
                if weather_obj.is_weather_chance(self.__request.requested):
                    response_type = "true"
                else:
                    response_type = "false"

        if answer_question:
            if response_type == "true":
                prefix = random.choice(self.__locale.general_answers["affirmative"]) + ", "
            elif response_type == "false":
                prefix = random.choice(self.__locale.general_answers["negative"]) + ", "

        if response_type == "false" or condition_type == ConditionType.UNKNOWN:
            suffix = " " + random.choice(self.__locale.general_answers["alternate_weather"])
        return (prefix + random.choice(self.__locale.condition_answers[condition_type][response_type]) + suffix).format(weather=output_conditions, when="{when}", where="{where}")

    @property
    def __output_date_and_time(self):
        log.debug(f"generating time and date for response")

        if self.__request.date_specified != "":
            date = self.__request.date_specified
        else:
            date = self.__locale.format_output_date(self.__request)
        if self.__request.time_specified != "":
            time = self.__request.time_specified
        else:
            if self.__request.grain == Grain.HOUR:
                time = self.__locale.format_output_time(self.__request)
            else:
                time = ""

        if self.__request.grain == Grain.HOUR:
            return date + " " + time
        return date

    @property
    def __output_location(self):
        log.debug(f"generating location for response")
        return self.__locale.format_output_location(self.__request.location.name) if self.__request.location_specified else ""

    @property
    def request(self):
        return self.__request
