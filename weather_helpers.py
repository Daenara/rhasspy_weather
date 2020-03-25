from enum import Enum

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
        
# my implementation of hermes-pythons Grain since that is the only thing I need from that package
class Grain(Enum):
    YEAR = 0
    QUARTER = 1
    MONTH = 2
    WEEK = 3
    DAY = 4
    HOUR = 5
    

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