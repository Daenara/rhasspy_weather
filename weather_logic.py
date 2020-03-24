# -*- encoding: utf-8 -*-
import datetime
import requests
import random
import suntime
from enum import Enum

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
        the weatherdata that should be used in the answer
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
            the weatherdata that should be used in the answer
        """

        self.forecast = forecast
        self.request = request
        self.error = forecast.error

    # generates the answer to a question about anything weather related (that
    # the programm supports)
    # called from outside
    def generate_report(self):
        """
        generates and returns the answer to the WeatherRequest as string
        If an error occurs it will return the error message as a string instead
        """

        #print("WeatherReport.generate_report - error_code=" + str(self.error.error_code))
        if self.error.error_code != 0:
            return self.error.output_error()
        if self.request.request_date == -1:
            self.error.error_code = 8 # Error: something is wrong with the date
            return self.error.output_error()
        elif self.request.request_date < datetime.datetime.now().date() or self.request.grain == Grain.HOUR and self.request.request_date == datetime.datetime.now().date() \
            and self.request.start_time < datetime.datetime.now().time():
            self.error.error_code = 6 # Error: can't request forecast for the past
            return self.error.output_error()
        elif not self.forecast.has_weather_for_date(self.request.request_date):
            if self.request.request_date == datetime.datetime.now().date():
                if self.forecast.has_weather_for_date(self.request.request_date + datetime.timedelta(days=1)):
                    pass
                else:
                    self.error.error_code = 7 # Error: day nearly over, no forecast in api response
                    return self.error.output_error()
            else:
                self.error.error_code = 3 # Error: to many days in advance
                return self.error.output_error()
        if self.request.forecast_type == ForecastType.TEMPERATURE:
            return self.__generate_temperature_report()
        elif self.request.forecast_type == ForecastType.CONDITION:
            return self.__generate_condition_report()
        elif self.request.forecast_type == ForecastType.FULL:
           return self.__generate_full_report()
        elif self.request.forecast_type == ForecastType.ITEM:
            return self.__generate_item_report()
    
    # returns the answer to a question about the weather
    # called by generate_report()
    def __generate_full_report(self):
        #print("  -> full_report - error_code=" + str(self.error.error_code))
        response = ""
        if self.request.date_type == DateType.FIXED:
            if self.request.grain == Grain.DAY:
                response = self.__generate_full_report_day()
            elif self.request.grain == Grain.HOUR:
                #print("     -> time - error_code=" + str(self.error.error_code))
                weather = self.forecast.weather_at_time(self.request.request_date, self.request.start_time)
                response = self.__answer_condition(weather).format(when=self.__output_date_and_time, where=self.__output_location)
                response = response + " " + self.__answer_temperature(weather.min_temperature).format(when="", where="")
            else:
                self.error.error_code = 4 # Error: not supported
                response = self.error.output_error()
        elif self.request.date_type == DateType.INTERVAL: 
            #print("     -> interval - error_code=" + str(self.error.error_code))
            weather = self.forecast.weather_for_interval(self.request.request_date, self.request.start_time, self.request.end_time)
            response = self.__answer_condition(weather).format(when=self.__output_date_and_time, where=self.__output_location)
            response = response + " " + self.__answer_temperature(weather.min_temperature, weather.max_temperature).format(when="", where="")
        return response

    # returns the answer to a question about the temperature
    # called by generate_report()
    def __generate_temperature_report(self):
        #print("  -> temperature_report - error_code=" + str(self.error.error_code))
        response = ""
        if self.request.date_type == DateType.FIXED:
            if self.request.grain == Grain.DAY:
                response = self.__generate_temperature_report_day()
            elif self.request.grain == Grain.HOUR:
                #print("     -> time - error_code=" + str(self.error.error_code))
                response = ""
                weather = self.forecast.weather_at_time(self.request.request_date, self.request.start_time)
                response = self.__answer_temperature(weather.min_temperature).format(when=self.__output_date_and_time, where=self.__output_location)
            else:
                self.error.error_code = 4 # Error: not supported
                response = self.error.output_error()
        elif self.request.date_type == DateType.INTERVAL: 
            #print("     -> interval - error_code=" + str(self.error.error_code))
            weather = self.forecast.weather_for_interval(self.request.request_date, self.request.start_time, self.request.end_time)
            response = self.__answer_temperature(weather.min_temperature, weather.max_temperature).format(when=self.__output_date_and_time, where=self.__output_location)
        return response

    # returns a string answer to a question about the weather condition
    # called by generate_report()
    def __generate_condition_report(self):
        #print("  -> condition_report - error_code=" + str(self.error.error_code))
        response = ""
        if self.request.date_type == DateType.FIXED:
            if self.request.grain == Grain.DAY:
                response = self.__generate_condition_report_day()
            elif self.request.grain == Grain.HOUR:
                #print("     -> time - error_code=" + str(self.error.error_code))
                weather_at_time = self.forecast.weather_at_time(self.request.request_date, self.request.start_time)
                response = self.__answer_condition(weather_at_time).format(when=self.__output_date_and_time, where=self.__output_location)
            else:
                self.error.error_code = 4 # Error: not supported
                response = self.error.output_error()
        elif self.request.date_type == DateType.INTERVAL: 
            #print("     -> interval - error_code=" + str(self.error.error_code))
            weather = self.forecast.weather_for_interval(self.request.request_date, self.request.start_time, self.request.end_time)
            response = self.__answer_condition(weather).format(when=self.__output_date_and_time, where=self.__output_location)
        return response

    # returns a string with the answer to the question about an item
    # called by generate_report()
    def __generate_item_report(self):
        #print("WeatherReport.generate_item_report - error_code=" + str(self.error.error_code))
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
        #print("     -> day - error_code=" + str(self.error.error_code))
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
        #print("     -> day - error_code=" + str(self.error.error_code))
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
        #print("     -> day - error_code=" + str(self.error.error_code))
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
        return "in {0}".format(self.request.location) if self.request.location else ""

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
    units : str
        the units the API should use
    location : Location
        a location object containing where the saved weather occurs
    Methods:
    get_weather_from_open_weather_map(weather_api_key)
        gets the weather from open weather map, parses it and saves it
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

    def __init__(self, units, location):
        """
        Parameters:
        units : str
            the units the API should use
        location : Location
            a location object containing where the saved weather occurs
        """

        self.error = Error()
        self.forecast = []
        self.units = units
        self.location = location
    
    # gets the weather from open weather map, parses the information
    # and saves it in this class
    def get_weather_from_open_weather_map(self, weather_api_key):
        """gets weather from openweathermap API and parses it
        Returns 0 is everything worked, if not returns the error code
        Parameters:
        weather_api_key : str
            API key for openweathermap
        """

        #print("WeatherForecast.get_weather_from_open_weather_map, error_code=" + str(self.error.error_code))
        if self.error.error_code != 0:
            return self.error.error_code
        if hasattr(self.location, "lat") and hasattr(self.location, "lon"):
            url_location = "lat={lat}&lon={lon}".format(lat=self.location.lat, lon=self.location.lon)
        elif hasattr(self.location, "zipcode") and hasattr(self.location, "country"):
            url_location = "zip={zip},{country_code}".format(zip=self.location.zipcode, country_code=self.location.country)
        else:
            url_location = "q={city_name}".format(city_name=self.location.name)
        forecast_url = "http://api.openweathermap.org/data/2.5/forecast?{location}&APPID={api_key}&units={units}&lang=de".format(\
            location=url_location, api_key=weather_api_key, units=self.units)
        try:
            response = requests.get(forecast_url)
            response = response.json()

            if response["cod"] == 401:
                self.error.error_code = 2 # Error: something went wrong with the api call
                return self.error.error_code
            elif response["cod"] == "429":
                self.error.error_code = 9 # Error: request limit exceeded
                return self.error.error_code
            elif response["cod"] == "404":
                self.error.error_code = 5 # Error: location not found
                return self.error.error_code
                
            # Parse the output of Open Weather Map's forecast endpoint
            if not (hasattr(self.location, "lat") and hasattr(self.location, "lon")):
                self.location.set_lat_and_lon(response["city"]["coord"]["lat"], response["city"]["coord"]["lon"])
            self.__calculate_sunrise_and_sunset()
            forecasts = {}
            for x in response["list"]:
                if str(datetime.date.fromtimestamp(x["dt"])) not in forecasts:
                    forecasts[str(datetime.date.fromtimestamp(x["dt"]))] = \
                        list(filter(lambda forecast: datetime.date.fromtimestamp(forecast["dt"]) == datetime.date.fromtimestamp(x["dt"]), response["list"]))
                    
            for key,forecast in forecasts.items():
                condition_list = []
                weather_condition = [x["weather"][0]["main"] for x in forecast]
                weather_description = [x["weather"][0]["description"] for x in forecast]
                weather_id = [x["weather"][0]["id"] for x in forecast]
                for x in range(len(weather_condition)):
                    temp_condition = WeatherCondition(self.__get_severity_from_open_weather_map_id(weather_id[x]), weather_description[x], weather_condition[x])
                    condition_list.append(temp_condition)
                tmp = WeatherForecast.WeatherAtDate(datetime.datetime.strptime(key, "%Y-%m-%d").date())
                tmp.parse_weather([datetime.datetime.strptime(x, "%H:%M:%S").time() for x in [x["dt_txt"].split(" ")[1] for x in forecast]],\
                   [x["main"]["temp"] for x in forecast], condition_list, [x["main"]["pressure"] for x in forecast],[x["main"]["humidity"] for x in forecast],\
                   [x["wind"]["speed"] for x in forecast],[x["wind"]["deg"] for x in forecast])
                self.forecast.append(tmp)
            ##print(*self.forecast, sep='\n')
            return 0
        except (requests.exceptions.ConnectionError, ValueError):
            self.error.error_code = 1 # Error: No internet connection
            return self.error.error_code 
    # parses the weather condition into my own format (WeatherConditon)
    def __get_severity_from_open_weather_map_id(self, id):
        if id == 210: return 0 # light thunderstorm
        if id == 211: return 1 # thunderstorm
        if id == 230: return 3 # thunderstorm with light drizzle
        if id == 231: return 4 # thunderstorm with drizzle
        if id == 232: return 5 # thunderstorm with heavy drizzle
        if id == 200: return 6 # thunderstorm with light rain
        if id == 201: return 7 # thunderstorm with rain
        if id == 202: return 8 # thunderstorm with heavy rain
        if id == 212: return 9 # heavy thunderstorm
        if id == 221: return 10 # ragged thunderstorm

        if id == 300: return 0 # light drizzle
        if id == 301: return 1 # drizzle
        if id == 321: return 1 # shower drizzle
        if id == 302: return 2 # heavy intensity drizzle
        if id == 310: return 3 # light intensity drizzle rain
        if id == 311: return 4 # drizzle rain
        if id == 312: return 5 # heavy intensity drizzle rain
        if id == 313: return 6 # shower rain and drizzle
        if id == 314: return 7 # heavy shower rain and drizzle

        if id == 500: return 0 # light rain
        if id == 520: return 0 # light intensity shower rain
        if id == 501: return 1 # moderate rain
        if id == 521: return 1 # shower rain
        if id == 511: return 1 # freezing rain
        if id == 502: return 2 # heavy intensity rain
        if id == 522: return 2 # heavy intensity shower rain
        if id == 503: return 3 # very heavy rain
        if id == 531: return 3 # ragged shower rain
        if id == 504: return 4 # extreme rain

        if id == 600: return 0 # light snow
        if id == 620: return 0 # light shower snow
        if id == 612: return 0 # light shower sleet
        if id == 615: return 1 # light rain and snow
        if id == 601: return 1 # snow
        if id == 621: return 1 # shower snow
        if id == 611: return 1 # sleet
        if id == 613: return 1 # shower sleet
        if id == 616: return 2 # rain and snow
        if id == 602: return 2 # heavy snow
        if id == 622: return 2 # heavy shower snow

        if id == 801: return 0 # few clouds: 11-25%
        if id == 802: return 1 # scattered clouds: 25-50%
        if id == 803: return 2 # broken clouds: 51-84%
        if id == 804: return 3 # overcast clouds: 85-100%
       
        return 0
    # calculates the time for sunrise and sunset
    def __calculate_sunrise_and_sunset(self):
        sun = suntime.Sun(self.location.lat, self.location.lon)
        self.sunrise = sun.get_local_sunrise_time().time()
        self.sunset = sun.get_local_sunset_time().time()
    # returns WeatherInterval for a request only during daylight hours
    def weather_during_daytime(self, request):
        """returns WeatherInterval for a request only during daylight hours
        Parameters:
        request : WeatherRequest
        """

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
    # returns the weather for a whole day
    def weather_for_day(self, date):
        """returns the weather for a whole day
        Parameters:
        date : datetime.date
        """

        weather = self.__get_forecast_for_date(date)
        return weather.get_weather_for_interval(datetime.time.min, datetime.time.max)
    # returns the weather at a specific time
    def weather_at_time(self, date, time):
        """returns the weather at a specific time
        Parameters:
            date : datetime.date
            time : datetime.time
        """

        weather = self.__get_forecast_for_date(date)
        return weather.get_weather_for_interval(time, time)
    # returns the weather for a time interval
    def weather_for_interval(self, date, start, end):
        """returns the weather for a time interval
        Parameters:
            date : datetime.date
            start : datetime.time
            end : datetime.time
        """
        weather = self.__get_forecast_for_date(date)
        return weather.get_weather_for_interval(start, end)
    # returns the weather for the morning of a day
    def weather_morning(self, date):
        """returns the weather during the morning of date
        Parameters:
        date : datetime.date
        """

        start = datetime.time(6,0)
        end = datetime.time(11,59)
        if date == datetime.datetime.now().date() and end < datetime.datetime.now().time():
            return None
        weather = self.__get_forecast_for_date(date)
        weather_for_interval = weather.get_weather_for_interval(start, end)
        weather_for_interval.switch = True
        return weather_for_interval
    # returns the weather for the noon of a day
    def weather_noon(self, date):
        """returns the weather during the noon of date
        Parameters:
        date : datetime.date
        """

        start = datetime.time(12,0)
        end = datetime.time(16,59)
        if date == datetime.datetime.now().date() and end < datetime.datetime.now().time():
            return None
        weather = self.__get_forecast_for_date(date)
        weather_for_interval = weather.get_weather_for_interval(start, end)
        weather_for_interval.switch = True
        return weather_for_interval
    # returns the weather for the evening of a day
    def weather_evening(self, date):
        """returns the weather during the evening of date
        Parameters:
        date : datetime.date
        """

        start = datetime.time(17,0)
        end = datetime.time(20,59)
        if date == datetime.datetime.now().date() and end < datetime.datetime.now().time():
            return None
        weather = self.__get_forecast_for_date(date)
        weather_for_interval = weather.get_weather_for_interval(start, end)
        weather_for_interval.switch = True
        return weather_for_interval
    # returns the weather for the night (at date and date+1)
    def weather_night(self, date):
        """returns the weather during the night of date and date+1
        Parameters:
        date : datetime.date
        """

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
        if self.error.error_code != 0:
            return self.error.error_code
        for x in self.forecast:
            if x.date == date:
                return x
        return None
    # checks if a forecast for date exists
    def has_weather_for_date(self, date):
        """checks if a forecast for date exists
        Returns True if it exists, else False
        Parameters:
        date : datetime.date
        """

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

##########  Weather Request ##########

# Class holding all the information that parse_intent_message found
# has many functions to return the information in
# human- and machinereadable ways
class WeatherRequest:
    """
    Class holding all the information that parse_intent_message found
    has many functions to return the information in 
    human- and machinereadable ways
    Attributes:
    date_type : DateType
        Is the request for a fixed time or an interval
    grain : Grain
        How specific should the request be, days, hours
    request_date : datetime.date
        For when is the request
    location : str
        For where is the request
    requested : str
        Was a specific condition, item or temperature requested
    time_specified : str
        non parsed time for the request (used for output)
    forecast_type : ForecastType
        Type of request, full, temperature, condition or item
    detail : bool
        True for detailed answer, else use False
    start_time : datetime.time
    end_time : datetime.time
    weekday : str
    string_date :str
    readable_date : str
    string_start_time : str
    readable_start_time : str
    string_end_time : str
    readable_end_time : str
    time_difference : int
        number of days between today and the requested date
    """

    def __init__(self, date_type, grain, request_date, forecast_type, detail):
        """
        Parameters:
        date_type : DateType
        grain : Grain
        request_date : datetime.date
        forecast_type : ForecastType
        detail : bool
        """
        self.date_type = date_type
        self.grain = grain
        self.request_date = request_date
        self.location = ""
        self.requested = ""
        self.time_specified = ""
        self.date_specified = ""
        self.forecast_type = forecast_type
        self.detail = detail
    
    def __str__(self): 
        return "(" + str(self.forecast_type) + ", " + str(self.date_type) + ", " + \
               str(self.grain) + ", " + self.string_date + ", " + str(self.start_time) + \
               ", " + str(self.end_time) + ", " + self.location + ", " + self.requested + ")"
    
    def __get_valid_time(self, val):
        if type(val) is datetime.time:
            time = val
        elif type(val) is str:
            try:
                time = datetime.datetime.strptime(val, "%H:%M:%S").time()
            except ValueError:
                hours, minutes, seconds = map(int, "00:00:00".split(':'))
                if hours >= 24 and 0 <= minutes < 60 and 0 <= seconds < 60: 
                    time = datetime.time(0,minutes,seconds)
        if time:
            # if the weather at midnight was requested change the day to the
            # next day
            # (snips thinks midnight means 00:00AM of the day requested, I say
            # it is after 11:59PM of the day requested)
            if self.grain == Grain.HOUR and time == datetime.time.min:
                self.request_date = self.request_date + datetime.timedelta(days=1)
            elif self.grain == Grain.HOUR and self.request_date == datetime.datetime.now().date() and \
                datetime.datetime.now().time() > time and time < datetime.time(12,0):
               return time.replace(hour=time.hour + 12)
            return time
        return -1 # somehing was wrong with the time
    
    @property
    def grain(self):
        return self.__grain
    @grain.setter
    def grain(self, val):
        if type(val) is Grain:
            self.__grain = val
    
    @property
    def date_type(self):
        return self.__date_type
    @date_type.setter
    def date_type(self, val):
        if type(val) is DateType:
            self.__date_type = val
    
    @property
    def forecast_type(self):
        return self.__forecast_type
    @forecast_type.setter
    def forecast_type(self, val):
        if type(val) is ForecastType:
            self.__forecast_type = val
    
    @property
    def request_date(self):
        return self.__request_date
    @request_date.setter
    def request_date(self, val):
        if type(val) is datetime.date:
            self.__request_date = val
        elif type(val) is str:
            self.__request_date = datetime.datetime.strptime(val, "%Y-%m-%d").date()
        else:
            self.__request_date = -1
    
    @property
    def start_time(self):
        if '_WeatherRequest__start_time' in self.__dict__:
            return self.__start_time
        return None
    @start_time.setter
    def start_time(self, val):
        self.__start_time = self.__get_valid_time(val)
        
    @property
    def end_time(self):
        if '_WeatherRequest__end_time' in self.__dict__:
            return self.__end_time
        return None
    @end_time.setter
    def end_time(self, val):
        self.__end_time = self.__get_valid_time(val)
    
    @property
    def weekday(self):
        return self.request_date.strftime("%A")
        
    @property
    def readable_date(self):
        return self.request_date.strftime("%d. %B")
        
    @property
    def string_date(self):
        return self.request_date.strftime("%Y-%m-%d")
        
    @property
    def string_start_time(self):
        return self.start_time.strftime("%H:%M:%S")
        
    @property
    def string_end_time(self):
        return self.end_time.strftime("%H:%M:%S")
    
    @property
    def readable_start_time(self):
        return self.start_time.strftime("%H:%M")
        
    @property
    def readable_end_time(self):
        return self.end_time.strftime("%H:%M")
        
    @property
    def time_difference(self):
        time_difference = (self.request_date - datetime.date.today()).days
        if self.grain == Grain.HOUR and self.start_time == datetime.time(0,0,0):
            return (time_difference - 1)
        return time_difference           

##########  Helper Classes ##########

# Class used by WeatherReport and WeatherForecast
# filled by WeatherForecast and used by WeatherReport
# to generate the answer to the request
class WeatherInterval:
    def __init__(self, switch=False):
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
        self.switch = switch

    # puts information into itself
    def add_information(self, weather_at_time):
        self.__change_count = self.__change_count + 1
        if weather_at_time.temperature > self.max_temperature:
            self.max_temperature = weather_at_time.temperature
        if weather_at_time.temperature < self.min_temperature:
            self.min_temperature = weather_at_time.temperature
        if weather_at_time.weather_condition_obj not in self.weather_condition_list:
            self.weather_condition_list.append(weather_at_time.weather_condition_obj)
        self.increase_counter(weather_at_time.weather_condition)

    # counts how many occurances of a certain weathertype there are
    def increase_counter(self, counter):
        if counter == "Rain" or counter == "Drizzle": 
            self.__rain = self.__rain + 1
        elif counter == "Thunderstorm":
            self.__thunderstorm = self.__thunderstorm + 1
        elif counter == "Snow":
            self.__snow = self.__snow + 1
        elif counter == "Clouds":
            self.__clouds = self.__clouds + 1
        elif counter == "Clear":
            self.__clear = self.__clear + 1
        elif counter == "Mist":
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

    # puts together the output string from the
    #conditions saved in weather_condition_list
    @property
    def weather_description(self):
        selected = []
        for x in self.weather_condition_list:
            if selected == []:
                selected.append(x)
            else:
                for y in selected:
                    if x.condition == y.condition:
                        if x.severity > y.severity:
                            selected.remove(y)
                            selected.append(x)
                    else:
                        if self.switch:
                            # clear sky and clouds in the same period of time
                            # seems fishy so lets remove the clear sky if we
                            # know about clouds
                            if y.condition == "Clear" and x.condition == "Clouds":
                                selected.remove(y)
                            # still fishy so if we already have clouds lets not
                            # add a clear sky
                            if not (x.condition == "Clear" and y.condition == "Clouds"):
                                selected.append(x)
                        else:
                            selected.append(x)
        description = ""
        for x in selected:
            if description == "":
                description = x.description
            else:
                description = description + " und " + x.description
        return description
# WeatherRequest for a fixed time or an interval?
class DateType(Enum):
    FIXED = "fixed"
    INTERVAL = "interval"
# What kind of WeatherRequest was made?
class ForecastType(Enum):
    FULL = "full"
    TEMPERATURE = "temperature"
    ITEM = "item"
    CONDITION = "condition"
# Datadump for a WeatherCondition
class WeatherCondition:
    def __init__(self, severity, description, condition):
        self.severity = severity
        self.description = description
        self.condition = condition

    def __eq__(self, other):
        return self.description == other.description
# Datadump for a Location
class Location:
    def __init__(self, location_name):
        self.name = location_name

    def set_lat_and_lon(self, lat, lon):
        self.lat = float(lat)
        self.lon = float(lon)

    def set_zipcode(self, zipcode, country):
        self.zipcode = zipcode
        self.country = country
class Grain(Enum):
    YEAR = 0
    QUARTER = 1
    MONTH = 2
    WEEK = 3
    DAY = 4
    HOUR = 5
    MINUTE = 6
    SECOND = 7
# Datadump for Errors
class Error:
    def __init__(self, error_code=0):
        self.error_code = error_code

    @property
    def error_code(self):
        return self.__error_code  
    @error_code.setter
    def error_code(self, val):
        self.__error_code = val

    def output_error(self):
        #print("It seems there was an error...")
        if self.error_code == 0:
            response = "Null bedeutet kein fehler, das hier sollte nicht passieren..."
        if self.error_code == 1:
            response = random.choice(["Es ist leider kein Internet verfügbar.",
                                      "Ich bin nicht mit dem Internet verbunden.",
                                      "Es ist kein Internet vorhanden."])
        elif self.error_code == 2:
            response = random.choice(["Das Wetter konnte nicht abgerufen werden. "+\
                                        "Vermutlich ist der API-Schlüssel ungültig.",
                                      "Fehler beim Abrufen. Der API-Schlüssel ist ungültig."])
        elif self.error_code == 3:
            response = random.choice(["So weit in die Zukunft kenne ich das Wetter nicht.",
                                      "Ich kann nicht soweit in die Zukunft sehen.",
                                      "Das Wetter für diesen Tag wurde noch nicht beschlossen.",
                                      "Dieses Datum liegt zu weit in der Zukunft."])
        elif self.error_code == 4:
            response = random.choice(["Diese Funktion wird noch nicht unterstützt.", 
                                      "Ich weiß nicht wie ich diese Anfrage verarbeiten soll."])
        elif self.error_code == 5:
            response = "Ich kann die angegebene Stadt nich finden. Vielleicht habe ich sie nicht richtig verstanden"
        elif self.error_code == 6:
            response = "Ich kann dir das Wetter aus der Vergangenheit leider nicht sagen."
        elif self.error_code == 7:
            response = "Es ist so kurz vor Mitternacht, dass ich das Wetter für heute nicht abrufen kann."
        elif self.error_code == 8:
            response = "Irgendwas stimmt mit dem Datum nicht."
        elif self.error_code == 9:
            response = "Mit diesem API-Schlüssel wurden zu viele Anfragen gesenden. Versuche es später erneut."
        else:
            response = random.choice(["Es ist ein Fehler aufgetreten.", "Hier ist ein Fehler aufgetreten."])
        #print("    Error Code:" + str(self.error_code) + " - " + response)
        return response