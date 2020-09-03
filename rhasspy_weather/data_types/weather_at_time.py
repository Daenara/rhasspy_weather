import datetime

from rhasspy_weather.data_types.condition import WeatherCondition, ConditionType, WindCondition


class WeatherAtTime:
    def __init__(self, date, time, temperature, main_condition, pressure, humidity, wind_speed, wind_direction, interval,
                 location):
        self.interval = interval
        self.date = date
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
