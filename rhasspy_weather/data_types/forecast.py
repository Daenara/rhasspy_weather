import datetime
import logging

from rhasspy_weather.data_types.condition import WeatherCondition, ConditionType, WindCondition
from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.interval import WeatherInterval
from rhasspy_weather.utils.utils import normal_round

log = logging.getLogger(__name__)


class WeatherForecast:
    """
    A class requesting and containing data from the API

    Attributes:
    forecast : list[WeatherAtDate]
        list containing all the information from the API
    config : WeatherConfig
        a configuration object
    sunrise : datetime.time
        time of the sunrise (only set after calculate_sunrise_and_sunset(lat, lon) was called)
    sunset : datetime.time
        time of the sunset (only set after calculate_sunrise_and_sunset(lat, lon) was called)
    Methods:
    calculate_sunrise_and_sunset(lat, lon)
        sets sunrise and sunset
    weather_during_daytime(request)
        returns WeatherInterval for a request only during daylight hours
    weather_for_day(date)
        returns the weather for a whole day
    weather_at_time(date, time)
        returns the weather at a specific time
    weather_for_interval(date, start, end)
        returns the weather for a time interval
    weather_morning(date)
        returns the weather during the morning of date
    weather_noon(date)
        returns the weather during the noon of date
    weather_evening(date)
        returns the weather during the evening of date
    weather_night(date)
        returns the weather during the night of date and date+1
    has_weather_for_date(date)
        checks if a forecast for date exists
    """

    def __init__(self):
        log.debug("initializing forecast")

        self.forecast = []
        self.__timezone = get_config().timezone
        self.sunset, self.sunrise = None, None

    def __str__(self):
        return self.forecast

    def weather_during_daytime(self, request):
        """returns WeatherInterval for a request only during daylight hours
        Parameters:
        request : WeatherRequest
        """
        log.debug(f"getting weather for daytime")

        start_time = self.sunrise
        end_time = self.sunset
        date = request.request_date

        if request.start_time is not None and self.sunrise <= request.start_time <= self.sunset:
            start_time = request.start_time
        if request.end_time is not None and self.sunrise <= request.end_time <= self.sunset:
            end_time = request.end_time

        if end_time < start_time:
            date = date + datetime.timedelta(days=1)

        return self.weather_for_interval(date, start_time, end_time)

    # TODO: use this
    def weather_during_nighttime(self, request):
        """returns WeatherInterval for a request only during nighttime hours
        Parameters:
        request : WeatherRequest
        """
        log.debug(f"getting weather for nighttime")

        start_time = self.sunset
        end_time = self.sunrise

        if request.start_time is not None and self.sunset <= request.start_time <= datetime.time.max:
            start_time = request.start_time
        if request.end_time is not None and datetime.time.min <= request.end_time <= self.sunrise:
            end_time = request.end_time

        return self.weather_for_interval(request.request_date, start_time, end_time)

    def weather_for_day(self, date):
        """returns the weather for a whole day
        Parameters:
        date : datetime.date
        """
        log.debug(f"getting weather for the whole day")

        return self.weather_for_interval(date, datetime.time.min, datetime.time.max)

    def weather_at_time(self, date, time):
        """returns the weather at a specific time
        Parameters:
            date : datetime.date
            time : datetime.time
        """
        log.debug(f"getting weather at a certain time")

        return self.weather_for_interval(date, time, time)

    def weather_for_interval(self, date, start, end):
        """returns the weather for a time interval
        Parameters:
            date : datetime.date
            start : datetime.time
            end : datetime.time
        """
        log.debug(f"getting weather for an interval")

        weather = self.__get_forecast_for_date(date)

        if end < start:
            if weather is not None:
                weather_interval = weather.get_weather_for_interval(start, datetime.time.max)
                weather = self.__get_forecast_for_date(date + datetime.timedelta(days=1))
                weather_interval = weather.get_weather_for_interval(datetime.time.min, end, weather_interval)
            else:
                weather = self.__get_forecast_for_date(date + datetime.timedelta(days=1))
                weather_interval = weather.get_weather_for_interval(datetime.time.min, end)
            return weather_interval
        return weather.get_weather_for_interval(start, end)

    # returns the forecast at the specified date
    def __get_forecast_for_date(self, date):
        log.debug(f"getting the complete forecast for a date")

        for x in self.forecast:
            if x.date == date:
                return x
        return None

    def has_weather_for_date(self, date):
        """checks if a forecast for date exists
        Returns True if it exists, else False
        Parameters:
        date : datetime.date
        """
        log.debug(f"checking if there is weather for the date")

        return self.__get_forecast_for_date(date) is not None

    # Subclasses

    # saves the weather data at a specific date (list of WeatherAtTime)
    class WeatherAtDate:
        def __init__(self, date, location):
            self.date = date
            self.weather = []
            self.interval = 3
            self.location = location

        def __str__(self):
            str_weather = ""
            for x in self.weather:
                str_weather = str_weather + str(x) + "\n"
            return self.string_date + ":\n" + str_weather

        def __repr__(self):
            return self.__str__()

        # saves the weather into a new WeatherAtTime Object and adds it to the
        # list
        def parse_weather(self, time, temperature, weather_condition_list, pressure, humidity, wind_speed, wind_direction):
            for x in range(len(time)):
                self.weather.append(self.WeatherAtTime(time[x], temperature[x], weather_condition_list[x], pressure[x], humidity[x], wind_speed[x], wind_direction[x], self.interval, self.location))

        # returns the weather during the specified interval
        def get_weather_for_interval(self, from_time, to_time, weather_for_interval=None):
            if weather_for_interval is None:
                weather_for_interval = WeatherInterval()
            elif type(weather_for_interval) == int:
                return weather_for_interval
            if self.entries > 0:
                for x in self.weather:
                    if from_time <= x.time < to_time or x.time <= from_time <= x.end_time:
                        weather_for_interval.add_information(x)
            if weather_for_interval.contains_information:
                return weather_for_interval

        @property
        def string_date(self):
            return self.date.strftime("%Y-%m-%d")

        @property
        def entries(self):
            return len(self.weather)

        # Subclasses

        # saves the weather data at a specific time
        class WeatherAtTime:
            def __init__(self, time, temperature, main_condition, pressure, humidity, wind_speed, wind_direction, interval, location):
                self.interval = interval
                self.time = time
                self.temperature = temperature
                self.main_condition = main_condition
                self.other_conditions = [WindCondition(wind_speed, wind_direction)]
                self.pressure = pressure
                self.humidity = humidity
                self.location = location
                if self.main_condition.condition_type == ConditionType.CLEAR:
                    if self.is_during_day:
                        self.other_conditions.append(WeatherCondition(0, "", ConditionType.SUN))
                    if self.is_during_night:
                        self.other_conditions.append(WeatherCondition(0, "", ConditionType.STARS))

            def __str__(self):
                return "[" + str(self.string_time) + ", " + str(self.temperature) + ", " + str(self.weather_condition) + \
                       ", " + str(self.weather_description) + ", " + str(self.pressure) + "]"

            def __repr__(self):
                return self.weather_condition

            @property
            def weather_condition(self):
                return self.main_condition.condition_type

            @property
            def weather_severity(self):
                return self.main_condition.severity

            @property
            def weather_description(self):
                return self.main_condition.description

            @property
            def time(self):
                return self.__time

            @time.setter
            def time(self, val):
                if type(val) is datetime.time:
                    self.__time = val
                elif type(val) is str:
                    self.__time = datetime.datetime.strptime(val, "%H:%M:%S").time()
                if self.__time.hour + self.interval > 23:
                    self.end_time = datetime.time.max
                else:
                    self.end_time = datetime.time(self.__time.hour + self.interval, 59)

            @property
            def string_time(self):
                return self.__time.strftime("%H:%M:%S")

            @property
            def is_during_day(self):
                return self.location.sunrise <= self.time <= self.location.sunset

            @property
            def is_during_night(self):
                return self.location.sunset <= self.time <= self.location.sunrise
