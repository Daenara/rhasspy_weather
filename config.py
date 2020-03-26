from rhasspy_weather.status import Status, StatusCode
from rhasspy_weather.helpers import Location
import configparser
import pytz
import shutil
import os
import logging

log = logging.getLogger(__name__)

class WeatherConfig:
    def __init__(self):
        self.status = Status()
        base_path = os.path.dirname(__file__)
        config_path = os.path.join(base_path, 'config.ini')
        default_config_path = os.path.join(base_path, 'config.default')
        config = configparser.ConfigParser(allow_no_value=True)
        if not os.path.isfile(config_path):
            log.info("No config found, creating config")
            shutil.copy(default_config_path, config_path)
        config.read(config_path)
        
        if not (config.has_section("General") and config.has_section("Location")):
            log.error("At least one required section is missing. Please refer to 'config.default' for an example config.")
            self.status.set_status(StatusCode.CONFIG_ERROR)
            return self
        
        section_name_general = "General"
        if config.has_section(section_name_general):
            section_general = config[section_name_general]
            self.__detail = self.__get_required_option(section_general, "level_of_detail", False, "bool")
            self.__units = self.__get_required_option(section_general, "units", "metric")
            self.__api = self.__get_required_option(section_general, "api", "openweathermap")
            self.__timezone = pytz.timezone(self.__get_required_option(section_general, "timezone", "Europe/Berlin"))
        else:
            log.error("Section [{0}] is missing from config. Please refer to 'config.default' for an example config.".format(section_name_general))
            self.status.set_status(StatusCode.CONFIG_ERROR)
            return self
            
        section_name_location = "Location"
        if config.has_section(section_name_location):
            section_location = config[section_name_location]
            self.__location = Location(self.__get_required_option(section_location, "city", "Berlin"))
            zipcode = section_location.get("zipcode")
            country_code = section_location.get("country_code")
            if not (zipcode == None or country_code == None):
                self.__location.set_zipcode(zipcode, country_code)
            lat = section_location.get("lat")
            lon = section_location.get("lon")
            if not ((lat == None or lon == None) or (lat == "" or lon == "")):
                self.__location.set_lat_and_lon(lat, lon)
        else:
            log.error("Section [{0}] is missing from config. Please refer to 'config.default' for an example config.".format(section_name_location))
            self.status.set_status(StatusCode.CONFIG_ERROR)
            return self
        
        if self.api == "openweathermap":
            has_error = False
            section_name_openweathermap = "OpenWeatherMap"
            if config.has_section(section_name_openweathermap):
                section_openweathermap = config[section_name_openweathermap]
                if "api_key" in section_openweathermap:
                    api_key = section_openweathermap.get("api_key")
                    if api_key == None:
                        has_error = True
                    else:
                        self.__api_key = api_key
                else:
                    has_error = True
                
                if has_error:
                    log.error("API is set to OpenWeatherMap yet no API-Key is found. Please refer to 'config.default' for an example config.")
            else:
                log.error("API is set to OpenWeatherMap yet no config section for that is found. Please refer to 'config.default' for an example config.")
                has_error = True
                
            if has_error:
                self.status.set_status(StatusCode.API_ERROR) # Error: something went wrong with the api call
                return self
        log.info("Config Loaded")
            
            
    @property
    def detail(self):
        return self.__detail
            
    @property
    def api(self):
        return self.__api
        
    @property
    def timezone(self):
        return self.__timezone
        
    @property
    def units(self):
        return self.__units
        
    @property
    def location(self):
        return self.__location
        
    @property
    def api_key(self):
        return self.__api_key
        
    def __get_required_option(self, section, option, default_value, data_type=""):
        if option in section:
            if data_type == "bool":
                temp = section.getboolean(option)
            elif data_type == "int":
                temp = section.getint(option)
            elif data_type == "float":
                temp = section.getfloat(option)
            else:
                temp = section.get(option)
            if option == None:
                log.warning("Setting '{0}' is present but has no value. Please refer to 'config.default' for an example config.".format(option))
                return default_value
            else:
                return temp
        log.warning("Setting '{0}' is missing from config. Please refer to 'config.default' for an example config.".format(option))
        return default_value
    