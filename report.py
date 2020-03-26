import datetime
import pytz
import random
from rhasspy_weather.helpers import DateType, ForecastType, Location, Grain
from rhasspy_weather.status import Status, StatusCode

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
        
        self.forecast = forecast
        self.request = request
        self.status = Status()

    def generate_report(self):
        """
        generates and returns the answer to the WeatherRequest as string
        If an error occurs it will return the error message as a string instead
        """
        log.debug("generating weather report - error: {0}".format(self.status.is_error))
        
        if self.request.request_date < datetime.datetime.now(pytz.timezone(self.request.timezone)).date() or self.request.grain == Grain.HOUR and self.request.request_date == datetime.datetime.now(pytz.timezone(self.request.timezone)).date() \
            and self.request.start_time < datetime.datetime.now(pytz.timezone(self.request.timezone)).time():
            log.debug("Can't get past weather, return with error message")
            self.status.set_status(StatusCode.PAST_WEATHER_ERROR) # Error: can't request forecast for the past
            return self.status.status_response()
        elif not self.forecast.has_weather_for_date(self.request.request_date):
            log.debug("No weather for today")
            if self.request.request_date == datetime.datetime.now(pytz.timezone(self.request.timezone)).date():
                if self.request.date_type == DateType.FIXED:
                    log.debug("only weather for one day was requested, we don't have weather for that day so return with error message")
                    self.status.set_status(StatusCode.NO_WEATHER_FOR_DAY_ERROR) # Error: day nearly over, no forecast in api response
                    return self.status.status_response()
                elif self.request.request_date == DateType.INTERVAL:
                    log.debug("handle intervals that span over night here")
                    self.status.set_status(StatusCode.NOT_IMPLEMENTED_ERROR)
                    return self.status.status_response()
                    #if self.forecast.has_weather_for_date(self.request.request_date + datetime.timedelta(days=1)):
                    #    log.debug("weather for tomorrow was requested as well so we are good to continue")
            else:
                self.status.set_status(StatusCode.FUTURE_WEATHER_ERROR) # Error: to many days in advance
                return self.status.status_response()
        
        if not (self.request.grain == Grain.DAY or self.request.grain == Grain.HOUR):
            self.status.set_status(StatusCode.NOT_IMPLEMENTED_ERROR)
            return self.status.status_response()
    
        if self.request.forecast_type == ForecastType.TEMPERATURE:
            response = self.__generate_temperature_report()
        elif self.request.forecast_type == ForecastType.CONDITION:
            response = self.__generate_condition_report()
        elif self.request.forecast_type == ForecastType.FULL:
           response = self.__generate_full_report()
        elif self.request.forecast_type == ForecastType.ITEM:
            response = self.__generate_item_report()

        return response
    
    # returns the answer to a question about the weather
    # called by generate_report()
    def __generate_full_report(self):
        log.debug("generating full report - error: {0}".format(self.status.is_error))
        response = ""
        if self.request.date_type == DateType.FIXED:
            if self.request.grain == Grain.DAY:
                response = self.__generate_full_report_day()
            elif self.request.grain == Grain.HOUR:
                weather = self.forecast.weather_at_time(self.request.request_date, self.request.start_time)
                response = self.__answer_condition(weather).format(when=self.__output_date_and_time, where=self.__output_location)
                response = response + " " + self.__answer_temperature(weather.min_temperature).format(when="", where="")
        elif self.request.date_type == DateType.INTERVAL: 
            weather = self.forecast.weather_for_interval(self.request.request_date, self.request.start_time, self.request.end_time)
            response = self.__answer_condition(weather).format(when=self.__output_date_and_time, where=self.__output_location)
            response = response + " " + self.__answer_temperature(weather.min_temperature, weather.max_temperature).format(when="", where="")
        return response

    # returns the answer to a question about the temperature
    # called by generate_report()
    def __generate_temperature_report(self):
        log.debug("generating temperature report - error: {0}".format(self.status.is_error))
        response = ""
        if self.request.date_type == DateType.FIXED:
            if self.request.grain == Grain.DAY:
                response = self.__generate_temperature_report_day()
            elif self.request.grain == Grain.HOUR:
                response = ""
                weather = self.forecast.weather_at_time(self.request.request_date, self.request.start_time)
                response = self.__answer_temperature(weather.min_temperature).format(when=self.__output_date_and_time, where=self.__output_location)
        elif self.request.date_type == DateType.INTERVAL: 
            weather = self.forecast.weather_for_interval(self.request.request_date, self.request.start_time, self.request.end_time)
            response = self.__answer_temperature(weather.min_temperature, weather.max_temperature).format(when=self.__output_date_and_time, where=self.__output_location)
        return response

    # returns a string answer to a question about the weather condition
    # called by generate_report()
    def __generate_condition_report(self):
        log.debug("generating condition report - error: {0}".format(self.status.is_error))
        response = ""
        if self.request.date_type == DateType.FIXED:
            if self.request.grain == Grain.DAY:
                response = self.__generate_condition_report_day()
            elif self.request.grain == Grain.HOUR:
                weather_at_time = self.forecast.weather_at_time(self.request.request_date, self.request.start_time)
                response = self.__answer_condition(weather_at_time).format(when=self.__output_date_and_time, where=self.__output_location)
        elif self.request.date_type == DateType.INTERVAL: 
            weather = self.forecast.weather_for_interval(self.request.request_date, self.request.start_time, self.request.end_time)
            response = self.__answer_condition(weather).format(when=self.__output_date_and_time, where=self.__output_location)
        return response

    # returns a string with the answer to the question about an item
    # called by generate_report()
    def __generate_item_report(self):
        log.debug("generating item report - error: {0}".format(self.status.is_error))
        rain = ["Regenmantel", "Schirm", "Gummistiefel", "Halbschuhe", "Kaputze", "Hut", "Regenschirm"]
        warm = ["Sonnenbrille", "Sonnencreme", "Sonnenschirm", "Kappe", "Sonnenhut", "Sandalen"]
        cold = ["Winterstiefel", "Mantel", "Schal", "Handschuhe", "Mütze"]
        item = self.request.requested
        if self.request.requested in ["Regenmantel", "Schirm", "Hut", "Sonnenhut", "Mantel", "Schal", "Sonnenschirm", "Regenschirm"]:
            item = "ein " + item + " ist"
        elif self.request.requested in ["Kaputze", "Kappe", "Mütze", "Sonnenbrille"]:
            item = "eine " + item + " ist"
        elif self.request.requested in ["Gummistiefel", "Halbschuhe", "Sandalen", "Handschuhe", "Winterstiefel"]:
            item = item + " sind"
        elif self.request.requested in ["Sonnencreme"]:
            item = item + " ist"
        response = ""
        if self.request.date_type == DateType.FIXED:
            if self.request.grain == Grain.DAY:
                weather = self.forecast.weather_for_day(self.request.request_date)
            elif self.request.grain == Grain.HOUR:
                weather = self.forecast.weather_at_time(self.request.request_date, self.request.start_time)
        elif self.request.date_type == DateType.INTERVAL:
            weather = self.forecast.weather_for_interval(self.request.request_date, self.request.start_time, self.request.end_time)
        if self.request.requested in rain:
            if weather.is_rain_chance:
                response = "Es könnte {when} {where} regnen, {item} keine schlechte Idee."
            else:
                response = "Es ist {when} {where} kein Regen gemeldet. {item} also vermutlich unnötig."
        elif self.request.requested in warm:
            day_weather = self.forecast.weather_during_daytime(self.request)
            if day_weather.is_clear:
                if weather.max_temperature >= 20:
                    response = "Es ist {when} warm {where} und tagsüber kommt die Sonne raus. {item} daher eine gute Idee."
                else:
                    response = "Es ist {when} {where} nicht sonderlich warm aber trotzdem sonnig. {item} vielleicht trotzdem nützlich."
            else:
                response = "Es ist {when} {where} nicht unbedingt sonnig. {item} vermutlich eher überflüssig."
        elif self.request.requested in cold:
            if weather.max_temperature < 5:
                response = "Es ist {when} kalt {where}. {item} daher eine gute Idee."
            else:
                response = "Es ist {when} {where} nicht sonderlich kalt. {item} daher eher unnötig."
        else:
            return "Ich bin mir nicht sicher, was ein " + self.request.requested + " ist, tut mir leid."
        return response.format(when=self.__output_date_and_time, where=self.__output_location, item=item)

    # returns a string response with the weatherforecast for a full day
    # if detail=True in the config this answer may be rather long
    # called by __generate_full_report()
    def __generate_full_report_day(self):
        log.debug("generating full day report - error: {0}".format(self.status.is_error))
        if self.request.detail:
            response = "Der Wetter-Bericht {when} {where}: ".format(when=self.__output_date_and_time,where=self.__output_location)
            morning = self.forecast.weather_morning(self.request.request_date)
            if morning is not None:
                response = response + self.__answer_condition(morning).format(when="Morgens", where="")
                response = response + " " + self.__answer_temperature(morning.min_temperature, morning.max_temperature).format(when="", where="") + " "
            noon = self.forecast.weather_noon(self.request.request_date)
            if noon is not None:
                response = response + self.__answer_condition(noon).format(when="Mittags", where="")
                response = response + " " + self.__answer_temperature(noon.min_temperature, noon.max_temperature).format(when="", where="") + " "
            evening = self.forecast.weather_evening(self.request.request_date)
            if evening is not None:
                response = response + self.__answer_condition(evening).format(when="Abends", where="")
                response = response + " " + self.__answer_temperature(evening.min_temperature, evening.max_temperature).format(when="", where="") + " "
            night = self.forecast.weather_night(self.request.request_date)
            if night is not None:
                response = response + self.__answer_condition(night).format(when="Nachts", where="")
                response = response + " " + self.__answer_temperature(night.min_temperature, night.max_temperature).format(when="", where="")
        else:
            weather_for_day = self.forecast.weather_for_day(self.request.request_date)
            response = self.__answer_condition(weather_for_day).format(when=self.__output_date_and_time, where=self.__output_location)
            response = response + " " + self.__answer_temperature(weather_for_day.min_temperature, weather_for_day.max_temperature).format(when="", where="")
        return response

    # returns a string response with the temperatures for a full day
    # if detail=True in the config this answer may be rather long
    # called by __generate_temperature_report()
    def __generate_temperature_report_day(self):
        log.debug("generating temperature day report - error: {0}".format(self.status.is_error))
        if self.request.detail:
            response = "Die Temperatur {when} {where}. ".format(when=self.__output_date_and_time,where=self.__output_location)
            morning = self.forecast.weather_morning(self.request.request_date)
            if morning is not None:
                response = response + " " + self.__answer_temperature(morning.min_temperature, morning.max_temperature).format(when="Morgens", where="") + " "
            noon = self.forecast.weather_noon(self.request.request_date)
            if noon is not None:
                response = response + " " + self.__answer_temperature(noon.min_temperature, noon.max_temperature).format(when="Mittags", where="") + " "
            evening = self.forecast.weather_evening(self.request.request_date)
            if evening is not None:
                response = response + " " + self.__answer_temperature(evening.min_temperature, evening.max_temperature).format(when="Abends", where="") + " "
            night = self.forecast.weather_night(self.request.request_date)
            if night is not None:
                response = response + " " + self.__answer_temperature(night.min_temperature, night.max_temperature).format(when="Nachts", where="")
        else:
            weather = self.forecast.weather_for_day(self.request.request_date)
            response = self.__answer_temperature(weather.min_temperature, weather.max_temperature).format(when=self.__output_date_and_time, where=self.__output_location)
        return response

    # returns a string response with the weatherconditions for a full day
    # if detail=True in the config this answer may be rather long
    # called by __generate_condition_report()
    def __generate_condition_report_day(self):
        log.debug("generating condition day report - error: {0}".format(self.status.is_error))
        if self.request.detail:
            response = "Das Wetter {when} {where}. ".format(when=self.__output_date_and_time,where=self.__output_location)
            morning = self.forecast.weather_morning(self.request.request_date)
            if morning is not None:
                response = response + self.__answer_condition(morning).format(when="Morgens", where="") + " "
            noon = self.forecast.weather_noon(self.request.request_date)
            if noon is not None:
                response = response + self.__answer_condition(noon).format(when="Mittags", where="") + " "
            evening = self.forecast.weather_evening(self.request.request_date)
            if evening is not None:
                response = response + self.__answer_condition(evening).format(when="Abends", where="") + " "
            night = self.forecast.weather_night(self.request.request_date)
            if night is not None:
                response = response + self.__answer_condition(night).format(when="Nachts", where="")
        else:
            weather = self.forecast.weather_for_day(self.request.request_date)
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
        weather = ["Das Wetter {when} {where}: {weather}.", 
                    "{when} {where} ist das Wetter: {weather}.", 
                    "Wetter {when} {where}: {weather}."]
        rain_true = ["Ja, {when} wird es {where} regnen.",
                     "Ja, {when} gibt es {where} Regen.",
                     "Ja, es regnet {when} {where}.",
                     "Ja, {when} regnet es {where}."]
        rain_false = ["Nein, es regnet {when} {where} nicht. Das Wetter ist: {weather}.",
                      "Nein, {when} regnet es {where} nicht. Stattdessen ist das Wetter: {weather}.",
                      "Nein, {when} gibt es keinen Regen {where}. Das Wetter ist: {weather}."]
        snow_true = ["Ja, {when} wird es {where} schneien.",
                     "Ja, {when} gibt es {where} Schnee.",
                     "Ja, es schneit {when} {where}.",
                     "Ja, {when} schneit es {where}."]
        snow_false = ["Nein, es schneit {when} {where} nicht. Das Wetter ist: {weather}.",
                      "Nein, {when} schneit es {where} nicht. Stattdessen ist das Wetter: {weather}.",
                      "Nein, {when} gibt es keinen Schnee {where}. Das Wetter ist: {weather}."]
        thunderstorm_true = ["Ja, {when} gibt es {where} Gewitter."]
        thunderstorm_false = ["Nein, {when} {where} gewittert es nicht. Das Wetter ist: {weather}."]
        cloud_true = ["Ja, {when} kann es {where} bewölkt sein."]
        cloud_false = ["Nein, {when} {where} ist es nicht bewölkt. Das Wetter ist: {weather}."]
        sun_true = ["Ja, {when} {where} scheint die Sonne."]
        sun_false = ["Nein, {when} {where} scheint keine Sonne. Das Wetter ist: {weather}."]
        mist_true = ["Ja, {when} {where} ist es neblig."]
        mist_false = ["Nein, {when} {where} ist es nicht neblig. Das Wetter ist: {weather}."]
        if self.request.forecast_type == ForecastType.CONDITION:
            if self.request.requested == "Regen":
                if weather_obj.is_rain_chance:
                    return random.choice(rain_true).format(when="{when}", where="{where}")
                else:
                    return random.choice(rain_false).format(weather=weather_obj.weather_description, when="{when}", where="{where}")
            elif self.request.requested == "Schnee":
                if weather_obj.is_rain_chance:
                    return random.choice(snow_true).format(when="{when}", where="{where}")
                else:
                    return random.choice(snow_false).format(weather=weather_obj.weather_description, when="{when}", where="{where}")
            elif self.request.requested == "Sonne":
                day_weather = self.forecast.weather_during_daytime(self.request)
                if day_weather is not None and day_weather.is_clear:
                    return random.choice(sun_true).format(when="{when}", where="{where}")
                else:
                    return random.choice(sun_false).format(weather=weather_obj.weather_description, when="{when}", where="{where}")
            elif self.request.requested == "Gewitter":
                if weather_obj.is_thunderstorm_chance:
                    return random.choice(thunderstorm_true).format(when="{when}", where="{where}")
                else:
                    return random.choice(thunderstorm_false).format(weather=weather_obj.weather_description, when="{when}", where="{where}")
            elif self.request.requested == "Nebel":
                if weather_obj.is_misty:
                    return random.choice(mist_true).format(when="{when}", where="{where}")
                else:
                    return random.choice(mist_false).format(weather=weather_obj.weather_description, when="{when}", where="{where}")
            elif self.request.requested == "Wolken":
                if weather_obj.is_cloudy:
                    return random.choice(cloud_true).format(when="{when}", where="{where}")
                else:
                    return random.choice(cloud_false).format(weather=weather_obj.weather_description, when="{when}", where="{where}")
        return random.choice(weather).format(weather=weather_obj.weather_description, when="{when}", where="{where}")

    @property
    def __output_date_and_time(self):
        log.debug("generating time and date for response - error: {0}".format(self.status.is_error))
        # set date and time to default values
        date = "am " + self.request.readable_date
        time = ""
        
        # check if the user wanted a specific time/date
        userdefined_date = False
        userdefined_time = False
        if self.request.date_specified != "":
            date = self.request.date_specified
            userdefined_date = True
        if self.request.time_specified != "":
            time = self.request.time_specified
            userdefined_time = True
            
        # make the output date more pretty if the user did not ask for something specific
        if not userdefined_date:
            # determine date
            if self.request.time_difference == 0:
                date = "heute"
            elif self.request.time_difference == 1:
                date = "morgen"
            else:
                temp_day = datetime.datetime.today().weekday() + self.request.time_difference
                if temp_day < 7:
                    date = "am " + self.request.weekday
                elif temp_day < 14:
                    date = "nächste Woche " + self.request.weekday
        # make the output time more pretty if the user did not ask for something specific
        if not userdefined_time:
            # determine time
            if self.request.grain == Grain.HOUR:
                time = "um " + self.request.readable_start_time + " Uhr"
        return date + " " + time

    @property
    def __output_location(self):
        log.debug("generating location for response - error: {0}".format(self.status.is_error))
        return "in {0}".format(self.request.location.name) if self.request.location_specified else ""