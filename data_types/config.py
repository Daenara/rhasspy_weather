import configparser
import logging
import os
import shutil
from pathlib import Path

import pytz

from .location import Location

log = logging.getLogger(__name__)


class WeatherConfig:
    def __init__(self):
        log.info("Loading config")
        base_path = str(Path(__file__).parent.parent)
        config_path = os.path.join(base_path, 'config.ini')
        default_config_path = os.path.join(base_path, 'config.default')
        config_parser = configparser.ConfigParser(allow_no_value=True)
        if not os.path.isfile(config_path):
            log.info("No config found, creating config")
            shutil.copy(default_config_path, config_path)
        config_parser.read(config_path)

        if not (config_parser.has_section("General") and config_parser.has_section("Location")):
            log.error("At least one required section is missing. Please refer to 'config.default' for an example config.")
            return None

        section_name_general = "General"
        if config_parser.has_section(section_name_general):
            section_general = config_parser[section_name_general]
            self.__detail = self.__get_required_option(section_general, "level_of_detail", False, "bool")
            self.__units = self.__get_required_option(section_general, "units", "metric")
            api = self.__get_required_option(section_general, "api", "openweathermap")
            try:
                name = "rhasspy_weather.api." + api
                self.__api = __import__(name, fromlist=[''])
            except:
                log.error("There is no module in the api folder that matches the api name in your config.")
                return None
            parser = self.__get_required_option(section_general, "parser", "rhasspy_intent")
            try:
                name = "rhasspy_weather.parser." + parser
                self.__parser = __import__(name, fromlist=[''])
            except:
                log.error("There is no module in the parser folder that matches the parser name in your config.")
                return None
            locale = self.__get_required_option(section_general, "locale", "german")
            try:
                name = "rhasspy_weather.languages." + locale
                self.__locale = __import__(name, fromlist=[''])
            except:
                log.error("There is no module in the locale folder that matches the locale name in your config.")
                return None
            self.__timezone = pytz.timezone(self.__get_required_option(section_general, "timezone", "Europe/Berlin"))
            self.__temp_warm_from = self.__get_required_option(section_general, "temp_warm", 20, "int")
            self.__temp_cold_to = self.__get_required_option(section_general, "temp_cold", 5, "int")
        else:
            log.error("Section [{0}] is missing from config. Please refer to 'config.default' for an example config.".format(section_name_general))
            return None

        section_name_location = "Location"
        if config_parser.has_section(section_name_location):
            section_location = config_parser[section_name_location]
            self.__location = Location(self.__get_required_option(section_location, "city", "Berlin"))
            zipcode = section_location.get("zipcode")
            country_code = section_location.get("country_code")
            if not (zipcode is None or country_code is None):
                self.__location.set_zipcode(zipcode, country_code)
            lat = section_location.get("lat")
            lon = section_location.get("lon")
            if not ((lat is None or lon is None) or (lat == "" or lon == "")):
                self.__location.set_lat_and_lon(lat, lon)
        else:
            log.error("Section [{0}] is missing from config. Please refer to 'config.default' for an example config.".format(section_name_location))
            return None

        if api == "openweathermap":
            has_error = False
            section_name_openweathermap = "OpenWeatherMap"
            if config_parser.has_section(section_name_openweathermap):
                section_openweathermap = config_parser[section_name_openweathermap]
                if "api_key" in section_openweathermap:
                    api_key = section_openweathermap.get("api_key")
                    if api_key is None:
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
                return None
        log.info("Config Loaded")

    @property
    def detail(self):
        return self.__detail

    @property
    def api(self):
        return self.__api

    @property
    def parser(self):
        return self.__parser

    @property
    def temperature_warm_from(self):
        return self.__temp_warm_from

    @property
    def temperature_cold_to(self):
        return self.__temp_cold_to

    @property
    def timezone(self):
        return self.__timezone

    @property
    def units(self):
        return self.__units

    @property
    def locale(self):
        return self.__locale

    @property
    def location(self):
        return self.__location

    @property
    def api_key(self):
        return self.__api_key

    @staticmethod
    def __get_required_option(section, option, default_value, data_type=""):
        if option in section:
            if data_type == "bool":
                temp = section.getboolean(option)
            elif data_type == "int":
                temp = section.getint(option)
            elif data_type == "float":
                temp = section.getfloat(option)
            else:
                temp = section.get(option)
            if option is None:
                log.warning("Setting '{0}' is present but has no value. Please refer to 'config.default' for an example config.".format(option))
                return default_value
            else:
                return temp
        log.warning("Setting '{0}' is missing from config. Please refer to 'config.default' for an example config.".format(option))
        return default_value


__config = None


def get_config():
    global __config
    if __config is None:
        __config = WeatherConfig()
    return __config
