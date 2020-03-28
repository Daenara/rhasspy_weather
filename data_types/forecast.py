from .interval import WeatherInterval
from .status import Status, StatusCode
from rhasspy_weather.globals import config
import suntime
import datetime

import logging

log = logging.getLogger(__name__)

##########  Weather Forecast ##########

# Class responsible for getting an forecast from an API and saving it
# in itself in my own weather format (a list of WeatherAtDate objects).
# has functions to get the weather at a specific day, time or interval
class WeatherForecast:
    """
    A class requesting and containing data from the API
    Attributes:
    error : Error
        keeps track of errors throughout the program execution
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
             
        self.status = Status()
        self.forecast = []
        from rhasspy_weather.globals import config
        self.__timezone = config.timezone
    
    # calculates the time for sunrise and sunset
    def calculate_sunrise_and_sunset(self, lat, lon):
        log.debug("Calculating Sunrise and Sunset - error: {0}".format(self.status.is_error))
        sun = suntime.Sun(lat, lon)
        self.sunrise = sun.get_local_sunrise_time().time()
        self.sunset = sun.get_local_sunset_time().time()

    def weather_during_daytime(self, request):
        """returns WeatherInterval for a request only during daylight hours
        Parameters:
        request : WeatherRequest
        """
        log.debug("getting weather for daylight time - error: {0}".format(self.status.is_error))

        weather = self.__get_forecast_for_date(request.request_date)
        if request.start_time is not None:
            if self.sunrise <= request.start_time <= self.sunset:
                if request.end_time is not None:
                    if self.sunrise <= request.end_time <= self.sunset:
                        return weather.get_weather_for_interval(request.start_time, request.end_time)
                    return weather.get_weather_for_interval(request.start_time, self.sunset)
                return weather.get_weather_for_interval(request.start_time, request.start_time)
            else:
                if request.end_time is not None:
                    if self.sunrise <= request.end_time <= self.sunset:
                        return weather.get_weather_for_interval(self.sunrise, request.end_time)
        else:
            return weather.get_weather_for_interval(self.sunrise, self.sunset)
    
    def weather_for_day(self, date):
        """returns the weather for a whole day
        Parameters:
        date : datetime.date
        """
        log.debug("getting weather for the whole day - error: {0}".format(self.status.is_error))

        weather = self.__get_forecast_for_date(date)
        return weather.get_weather_for_interval(datetime.time.min, datetime.time.max)

    def weather_at_time(self, date, time):
        """returns the weather at a specific time
        Parameters:
            date : datetime.date
            time : datetime.time
        """
        log.debug("getting weather at a certain time - error: {0}".format(self.status.is_error))
        
        weather = self.__get_forecast_for_date(date)
        return weather.get_weather_for_interval(time, time)

    def weather_for_interval(self, date, start, end):
        """returns the weather for a time interval
        Parameters:
            date : datetime.date
            start : datetime.time
            end : datetime.time
        """
        log.debug("getting weather for an interval - error: {0}".format(self.status.is_error))
        
        weather = self.__get_forecast_for_date(date)
        return weather.get_weather_for_interval(start, end)

    def weather_morning(self, date):
        """returns the weather during the morning of date
        Parameters:
        date : datetime.date
        """
        log.debug("getting weather for the morning - error: {0}".format(self.status.is_error))

        start = datetime.time(6,0)
        end = datetime.time(11,59)
        if date == datetime.datetime.now(self.__timezone.timezone).date() and end < datetime.datetime.now(self.__timezone.timezone).time():
            return None
        weather = self.__get_forecast_for_date(date)
        weather_for_interval = weather.get_weather_for_interval(start, end)
        weather_for_interval.switch = True
        return weather_for_interval

    def weather_noon(self, date):
        """returns the weather during the noon of date
        Parameters:
        date : datetime.date
        """
        log.debug("getting weather for noon - error: {0}".format(self.status.is_error))

        start = datetime.time(12,0)
        end = datetime.time(16,59)
        if date == datetime.datetime.now(self.__timezone.timezone).date() and end < datetime.datetime.now(self.__timezone.timezone).time():
            return None
        weather = self.__get_forecast_for_date(date)
        weather_for_interval = weather.get_weather_for_interval(start, end)
        weather_for_interval.switch = True
        return weather_for_interval

    def weather_evening(self, date):
        """returns the weather during the evening of date
        Parameters:
        date : datetime.date
        """
        log.debug("getting weather for the evening - error: {0}".format(self.status.is_error))

        start = datetime.time(17,0)
        end = datetime.time(20,59)
        if date == datetime.datetime.now(self.__timezone.timezone).date() and end < datetime.datetime.now(self.__timezone.timezone).time():
            return None
        weather = self.__get_forecast_for_date(date)
        weather_for_interval = weather.get_weather_for_interval(start, end)
        weather_for_interval.switch = True
        return weather_for_interval

    def weather_night(self, date):
        """returns the weather during the night of date and date+1
        Parameters:
        date : datetime.date
        """
        log.debug("getting weather for the night - error: {0}".format(self.status.is_error))

        start = datetime.time(21,0)
        end = datetime.time(5,59)
        if self.has_weather_for_date(date) == True:
            part_one = self.__get_forecast_for_date(date).get_weather_for_interval(start, datetime.time.max)
            if self.has_weather_for_date(date + datetime.timedelta(days=1)) == True:
                part_two = self.__get_forecast_for_date(date + datetime.timedelta(days=1)).get_weather_for_interval(datetime.time.min, end, part_one)
                part_two.switch = True
                return part_two
            part_one.switch = True
            return part_one
        elif self.has_weather_for_date(date + datetime.timedelta(days=1)) == True:
            part_two = self.__get_forecast_for_date(date + datetime.timedelta(days=1)).get_weather_for_interval(datetime.time.min, end)
            part_two.switch = True
            return part_two       

    # returns the forecast at the specified date
    def __get_forecast_for_date(self, date):
        log.debug("getting the complete forecast for a date - error: {0}".format(self.status.is_error))
        if self.status.is_error:
            return self.status
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
        log.debug("checking if there is weather for the date - error: {0}".format(self.status.is_error))

        return self.__get_forecast_for_date(date) is not None
        
####  Classes ####

    # saves the weather data at a specific date (list of WeatherAtTime)
    class WeatherAtDate:
        def __init__(self, date):
            self.date = date
            self.weather = []
            self.interval = 3
        
        def __str__(self): 
            str_weather = ""
            for x in self.weather:
                str_weather = str_weather + str(x) + "\n"
            return self.string_date + ":\n" + str_weather
        # saves the weather into a new WeatherAtTime Object and adds it to the
        # list
        def parse_weather(self, time, temperature, weather_condition_list, pressure, humidity, wind_speed, wind_direction):
            for x in range(len(time)):
                self.weather.append(WeatherForecast.WeatherAtDate.WeatherAtTime(time[x], temperature[x], weather_condition_list[x], \
                    pressure[x], humidity[x], wind_speed[x], wind_direction[x], self.interval))
        
        # returns the weather during the specified interval
        def get_weather_for_interval(self, from_time, to_time, weather_for_interval=None):
            if weather_for_interval == None:
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
    
        ####  Classes ####
        
        # saves the weather data at a specific time
        class WeatherAtTime:
            def __init__(self, time, temperature, weather_condition_obj, pressure, humidity, wind_speed, wind_direction, interval):
                self.interval = interval
                self.time = time 
                self.temperature = temperature
                self.weather_condition_obj = weather_condition_obj
                self.pressure = pressure
                self.humidity = humidity
                self.wind_speed = wind_speed
                self.wind_direction = wind_direction
                
            def __str__(self): 
                return "[" + str(self.string_time) + ", " + str(self.temperature) + ", " + str(self.weather_condition) + \
                    ", " + str(self.weather_description) + ", " + str(self.pressure) + ", " + str(self.wind_speed) + ", " + str(self.wind_direction) + "]"

            @property
            def weather_condition(self):
                return self.weather_condition_obj.condition

            @property
            def weather_serveity(self):
                return self.weather_condition_obj.severity

            @property
            def weather_description(self):
                return self.weather_condition_obj.description

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