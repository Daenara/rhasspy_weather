import datetime
import random
from .request import DateType, ForecastType, Grain
from .location import Location
from .status import Status, StatusCode

import logging

log = logging.getLogger(__name__)

##########  Weather Report ##########

# Class that takes a WeatherRequest and a WeatherForecast
# and returns an answer
class WeatherReport:
    """
    A class that generates a weather report out of a WeatherRequest
    and a WeatherForecast object.
    Attributes:
    request : WeatherRequest
        the request to be answered
    forecast : WeatherForecast
        the weather data that should be used in the answer
    error : Error
        keeps track of errors throughout the program execution
        (reuses the Error object from forecast)
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
        
        self.__forecast = forecast
        self.__request = request
        from rhasspy_weather.globals import config
        self.__timezone = config.timezone
        self.__locale = config.locale
        self.status = Status()

    def generate_report(self):
        """
        generates and returns the answer to the WeatherRequest as string
        If an error occurs it will return the error message as a string instead
        """
        log.debug("generating weather report - error: {0}".format(self.status.is_error))
        
        if self.__request.request_date < datetime.datetime.now(self.__timezone).date() or self.__request.grain == Grain.HOUR and self.__request.request_date == datetime.datetime.now(self.__timezone).date() \
            and self.__request.start_time < datetime.datetime.now(self.__timezone).time():
            log.debug("Can't get past weather, return with error message")
            self.status.set_status(StatusCode.PAST_WEATHER_ERROR)
            return self.status.status_response()
        elif not self.__forecast.has_weather_for_date(self.__request.request_date):
            log.debug("No weather for today")
            if self.__request.request_date == datetime.datetime.now(self.__timezone).date():
                if self.__request.date_type == DateType.FIXED:
                    log.debug("only weather for one day was requested, we don't have weather for that day so return with error message")
                    self.status.set_status(StatusCode.NO_WEATHER_FOR_DAY_ERROR) # Error: day nearly over, no forecast in api response
                    return self.status.status_response()
                elif self.__request.request_date == DateType.INTERVAL:
                    log.debug("handle intervals that span over night here")
                    self.status.set_status(StatusCode.NOT_IMPLEMENTED_ERROR)
                    return self.status.status_response()
                    #if self.__forecast.has_weather_for_date(self.__request.request_date + datetime.timedelta(days=1)):
                    #    log.debug("weather for tomorrow was requested as well so we are good to continue")
            else:
                self.status.set_status(StatusCode.FUTURE_WEATHER_ERROR)
                return self.status.status_response()
        
        if not (self.__request.grain == Grain.DAY or self.__request.grain == Grain.HOUR):
            self.status.set_status(StatusCode.NOT_IMPLEMENTED_ERROR)
            return self.status.status_response()
    
        if self.__request.forecast_type == ForecastType.TEMPERATURE:
            response = self.__generate_temperature_report()
        elif self.__request.forecast_type == ForecastType.CONDITION:
            response = self.__generate_condition_report()
        elif self.__request.forecast_type == ForecastType.FULL:
           response = self.__generate_full_report()
        elif self.__request.forecast_type == ForecastType.ITEM:
            response = self.__generate_item_report()

        return response
    
    # returns the answer to a question about the weather
    # called by generate_report()
    def __generate_full_report(self):
        log.debug("generating full report - error: {0}".format(self.status.is_error))
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
        log.debug("generating temperature report - error: {0}".format(self.status.is_error))
        response = ""
        if self.__request.date_type == DateType.FIXED:
            if self.__request.grain == Grain.DAY:
                response = self.__generate_temperature_report_day()
            elif self.__request.grain == Grain.HOUR:
                response = ""
                weather = self.__forecast.weather_at_time(self.__request.request_date, self.__request.start_time)
                response = self.__answer_temperature(weather.min_temperature).format(when=self.__output_date_and_time, where=self.__output_location)
        elif self.__request.date_type == DateType.INTERVAL: 
            weather = self.__forecast.weather_for_interval(self.__request.request_date, self.__request.start_time, self.__request.end_time)
            response = self.__answer_temperature(weather.min_temperature, weather.max_temperature).format(when=self.__output_date_and_time, where=self.__output_location)
        return response

    # returns a string answer to a question about the weather condition
    # called by generate_report()
    def __generate_condition_report(self):
        log.debug("generating condition report - error: {0}".format(self.status.is_error))
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
        log.debug("generating item report - error: {0}".format(self.status.is_error))

        item = self.__request.requested
        
        if self.__request.date_type == DateType.FIXED:
            if self.__request.grain == Grain.DAY:
                weather = self.__forecast.weather_for_day(self.__request.request_date)
            elif self.__request.grain == Grain.HOUR:
                weather = self.__forecast.weather_at_time(self.__request.request_date, self.__request.start_time)
        elif self.__request.date_type == DateType.INTERVAL:
            weather = self.__forecast.weather_for_interval(self.__request.request_date, self.__request.start_time, self.__request.end_time)
        
        
        if self.__request.requested in self.__locale.rain_items:
            if weather.is_rain_chance:
                response_type = "rain"
            else:
                response_type = "no_rain"
        elif self.__request.requested in self.__locale.warm_items:
            day_weather = self.__forecast.weather_during_daytime(self.__request)
            if day_weather.is_clear:
                if weather.max_temperature >= 20:
                    response_type = "warm_and_sunny"
                else:
                    response_type = "not_warm_and_sunny"
            else:
                response_type = "not_sunny"
        elif self.__request.requested in self.__locale.cold_items:
            if weather.max_temperature < 5:
                response_type = "cold"
            else:
                response_type = "not_cold"
        else:
            response_type = "unknown_items"
        return random.choice(self.__locale.item_answers[response_type]).format(when=self.__output_date_and_time, where=self.__output_location, item=self.__locale.format_item_for_output(item))

    # returns a string response with the weatherforecast for a full day
    # if detail=True in the config this answer may be rather long
    # called by __generate_full_report()
    def __generate_full_report_day(self):
        log.debug("generating full day report - error: {0}".format(self.status.is_error))
        if self.__request.detail:
            response = "Der Wetter-Bericht {when} {where}: ".format(when=self.__output_date_and_time,where=self.__output_location)
            morning = self.__forecast.weather_morning(self.__request.request_date)
            if morning is not None:
                response = response + self.__answer_condition(morning).format(when="Morgens", where="")
                response = response + " " + self.__answer_temperature(morning.min_temperature, morning.max_temperature).format(when="", where="") + " "
            noon = self.__forecast.weather_noon(self.__request.request_date)
            if noon is not None:
                response = response + self.__answer_condition(noon).format(when="Mittags", where="")
                response = response + " " + self.__answer_temperature(noon.min_temperature, noon.max_temperature).format(when="", where="") + " "
            evening = self.__forecast.weather_evening(self.__request.request_date)
            if evening is not None:
                response = response + self.__answer_condition(evening).format(when="Abends", where="")
                response = response + " " + self.__answer_temperature(evening.min_temperature, evening.max_temperature).format(when="", where="") + " "
            night = self.__forecast.weather_night(self.__request.request_date)
            if night is not None:
                response = response + self.__answer_condition(night).format(when="Nachts", where="")
                response = response + " " + self.__answer_temperature(night.min_temperature, night.max_temperature).format(when="", where="")
        else:
            weather_for_day = self.__forecast.weather_for_day(self.__request.request_date)
            response = self.__answer_condition(weather_for_day).format(when=self.__output_date_and_time, where=self.__output_location)
            response = response + " " + self.__answer_temperature(weather_for_day.min_temperature, weather_for_day.max_temperature).format(when="", where="")
        return response

    # returns a string response with the temperatures for a full day
    # if detail=True in the config this answer may be rather long
    # called by __generate_temperature_report()
    def __generate_temperature_report_day(self):
        log.debug("generating temperature day report - error: {0}".format(self.status.is_error))
        if self.__request.detail:
            response = "Die Temperatur {when} {where}. ".format(when=self.__output_date_and_time,where=self.__output_location)
            morning = self.__forecast.weather_morning(self.__request.request_date)
            if morning is not None:
                response = response + " " + self.__answer_temperature(morning.min_temperature, morning.max_temperature).format(when="Morgens", where="") + " "
            noon = self.__forecast.weather_noon(self.__request.request_date)
            if noon is not None:
                response = response + " " + self.__answer_temperature(noon.min_temperature, noon.max_temperature).format(when="Mittags", where="") + " "
            evening = self.__forecast.weather_evening(self.__request.request_date)
            if evening is not None:
                response = response + " " + self.__answer_temperature(evening.min_temperature, evening.max_temperature).format(when="Abends", where="") + " "
            night = self.__forecast.weather_night(self.__request.request_date)
            if night is not None:
                response = response + " " + self.__answer_temperature(night.min_temperature, night.max_temperature).format(when="Nachts", where="")
        else:
            weather = self.__forecast.weather_for_day(self.__request.request_date)
            response = self.__answer_temperature(weather.min_temperature, weather.max_temperature).format(when=self.__output_date_and_time, where=self.__output_location)
        return response

    # returns a string response with the weatherconditions for a full day
    # if detail=True in the config this answer may be rather long
    # called by __generate_condition_report()
    def __generate_condition_report_day(self):
        log.debug("generating condition day report - error: {0}".format(self.status.is_error))
        if self.__request.detail:
            response = "Das Wetter {when} {where}. ".format(when=self.__output_date_and_time,where=self.__output_location)
            morning = self.__forecast.weather_morning(self.__request.request_date)
            if morning is not None:
                response = response + self.__answer_condition(morning).format(when="Morgens", where="") + " "
            noon = self.__forecast.weather_noon(self.__request.request_date)
            if noon is not None:
                response = response + self.__answer_condition(noon).format(when="Mittags", where="") + " "
            evening = self.__forecast.weather_evening(self.__request.request_date)
            if evening is not None:
                response = response + self.__answer_condition(evening).format(when="Abends", where="") + " "
            night = self.__forecast.weather_night(self.__request.request_date)
            if night is not None:
                response = response + self.__answer_condition(night).format(when="Nachts", where="")
        else:
            weather = self.__forecast.weather_for_day(self.__request.request_date)
            response = self.__answer_condition(weather).format(when=self.__output_date_and_time, where=self.__output_location)
        return response

    # returns a string with the temperature and placeholders for location and
    # time
    def __answer_temperature(self, min_temp, max_temp=""):
        log.debug("generating response for temperature - error: {0}".format(self.status.is_error))
        temperature_fix = ["Die Temperatur {when} {where} ist {temp} Grad.", 
                            "Es hat {where} {temp} Grad {when}.", 
                            "Es hat {where} {when} {temp} Grad.", 
                            "Es hat {when} {temp} Grad {where}."]
        temperature_minmax = ["Die Temperatur {when} {where} ist zwischen {min} und {max} Grad. ",
                              #"Die Höchsttemperatur wird {when} {where} {max}
                              #Grad sein und die Tiefsttemperatur {min} Grad.",
                              "{when} {where} Temperaturen zwischen {min} und {max} Grad.",
                              "Die Temperatur {when} {where} liegt zwischen {min} und {max} Grad. "]
        if max_temp == "":
            max_temp = min_temp
        min_temp = int(min_temp)
        max_temp = int(max_temp)
        if min_temp == max_temp:
            return random.choice(temperature_fix).format(temp=min_temp, when="{when}", where="{where}")
        else:
            return random.choice(temperature_minmax).format(min=min_temp, max=max_temp, when="{when}", where="{where}")

    # returns a string with the weather condition and placeholders for location
    # and time
    def __answer_condition(self, weather_obj):
        log.debug("generating response for condition - error: {0}".format(self.status.is_error))
        from rhasspy_weather.data_types.condition import ConditionType
        if self.__request.forecast_type == ForecastType.CONDITION:
            output_conditions = self.__locale.combine_conditions(weather_obj.get_output_condition_list())
            log.debug(output_conditions)
            if self.__request.requested == ConditionType.RAIN:
                if weather_obj.is_rain_chance:
                    response_type = "rain_true"
                else:
                    response_type = "rain_false"
            elif self.__request.requested == ConditionType.SNOW:
                if weather_obj.is_snow_chance:
                    response_type = "snow_true"
                else:
                    response_type = "snow_false"
            elif self.__request.requested == ConditionType.CLEAR:
                day_weather = self.__forecast.weather_during_daytime(self.__request)
                if day_weather is not None and day_weather.is_clear:
                    response_type = "sun_true"
                else:
                    response_type = "sun_false"
            elif self.__request.requested == ConditionType.THUNDERSTORM:
                if weather_obj.is_thunderstorm_chance:
                    response_type = "thunderstorm_true"
                else:
                    response_type = "thunderstorm_false"
            elif self.__request.requested == ConditionType.MIST:
                if weather_obj.is_misty:
                    response_type = "mist_true"
                else:
                    response_type = "mist_false"
            elif self.__request.requested == ConditionType.CLOUDS:
                if weather_obj.is_cloudy:
                    response_type = "clouds_true"
                else:
                    response_type = "clouds_false"
            elif self.__request.requested == ConditionType.WIND:
                log.error("condition wind not implemented yet")
                self.status.set_status(StatusCode.NOT_IMPLEMENTED_ERROR)
                return self.status.status_response()
            elif self.__request.requested == ConditionType.UNKNOWN:
                response_type = "unknown_condition"
            else:
                response_type = "general_weather"
  
        return random.choice(self.__locale.condition_answers[response_type]).format(weather=output_conditions, when="{when}", where="{where}")

    @property
    def __output_date_and_time(self):
        log.debug("generating time and date for response - error: {0}".format(self.status.is_error))
        # set date and time to default values
        date = "am " + self.__request.readable_date
        time = ""
        
        # check if the user wanted a specific time/date
        userdefined_date = False
        userdefined_time = False
        if self.__request.date_specified != "":
            date = self.__request.date_specified
            userdefined_date = True
        if self.__request.time_specified != "":
            time = self.__request.time_specified
            userdefined_time = True
            
        # make the output date more pretty if the user did not ask for something specific
        if not userdefined_date:
            # determine date
            if self.__request.time_difference == 0:
                date = "heute"
            elif self.__request.time_difference == 1:
                date = "morgen"
            else:
                temp_day = datetime.datetime.today().weekday() + self.__request.time_difference
                if temp_day < 7:
                    date = "am " + self.__request.weekday
                elif temp_day < 14:
                    date = "nächste Woche " + self.__request.weekday
        # make the output time more pretty if the user did not ask for something specific
        if not userdefined_time:
            # determine time
            if self.__request.grain == Grain.HOUR:
                time = "um " + self.__request.readable_start_time + " Uhr"
                
        if self.__request.grain == Grain.HOUR:
            return date + " " + time
        return date

    @property
    def __output_location(self):
        log.debug("generating location for response - error: {0}".format(self.status.is_error))
        return "in {0}".format(self.__request.location.name) if self.__request.location_specified else ""