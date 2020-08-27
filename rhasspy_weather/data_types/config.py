import configparser
import logging
import os
from pathlib import Path

import pytz

from rhasspy_weather.data_types.error import ConfigError
from rhasspy_weather.data_types.location import Location

log = logging.getLogger(__name__)
config_path = os.path.join(str(Path(__file__).parent.parent.parent), 'config.ini')

config_sections = {
    "General": "__parse_section_general",
    "Weather": "__parse_section_weather",
    "Location": "__parse_section_location"
}


class WeatherConfig:

    def __init__(self, current_config_path):
        log.info("Loading config")

        self.__api = None
        self.__parser = None
        self.__output = None
        self.__output_template = None
        self.units = None
        self.timezone = None
        self.__locale = None

        self.temp_warm_from = None,
        self.temp_cold_to = None
        self.detail = None

        self.location = None

        self.__config_parser = configparser.ConfigParser(allow_no_value=True)
        self.__config_parser.read(current_config_path)

        for section, function_string in config_sections.items():
            getattr(self, "_WeatherConfig" + function_string)(self.__config_parser[section])

        log.info("Config Loaded")

    def __parse_section_general(self, section):
        if section is None:
            log.error(f"Required section {section} is missing. Please refer to 'config.default' for an example config.")

        self.locale = self.__get_option_with_default_value(section, "locale", "german")
        self.units = self.__get_option_with_default_value(section, "units", "metric")
        self.api = self.__get_option_with_default_value(section, "api", "openweathermap")
        self.api.parse_config(self.__config_parser)
        self.parser = self.__get_option_with_default_value(section, "parser", "rhasspy_intent")
        self.output = self.__get_option_with_default_value(section, "output", "console_json").replace(" ", "").split(",")
        self.output_template = self.__get_option_with_default_value(section, "output_template", "rhasspy.json")
        self.timezone = pytz.timezone(self.__get_option_with_default_value(section, "timezone", "Europe/Berlin"))

    def __parse_section_weather(self, section):
        if section is None:
            log.error(f"Required section {section} is missing. Please refer to 'config.default' for an example config.")

        self.temp_warm_from = self.__get_option_with_default_value(section, "temp_warm", 20, "int")
        self.temp_cold_to = self.__get_option_with_default_value(section, "temp_cold", 5, "int")
        self.detail = self.__get_option_with_default_value(section, "level_of_detail", False, "bool")

    def __parse_section_location(self, section):
        if section is None:
            log.error(f"Required section {section} is missing. Please refer to 'config.default' for an example config.")

        self.location = self.__get_option_with_default_value(section, "city", "Berlin"), section.get("zipcode"), section.get("country_code"), section.get("lat"), section.get("lon")

    @property
    def api(self):
        return self.__api

    @api.setter
    def api(self, val: str):
        if val is None or val is "":
            raise ConfigError("API Error", "API is set to OpenWeatherMap yet no API-Key is found. Please refer to 'config.default' for an example config.")
        try:
            self.__api = __import__("rhasspy_weather.api." + val, fromlist=[''])
        except ImportError:
            raise ConfigError("No api found", "There is no module in the api folder that matches the api name in your config.")

    @property
    def parser(self):
        return self.__parser

    @parser.setter
    def parser(self, val):
        try:
            self.__parser = __import__("rhasspy_weather.parser." + val, fromlist=[''])
        except ImportError:
            raise ConfigError("No parser found", "There is no module in the parser folder that matches the parser name in your config.")

    @property
    def output(self):
        return self.__output

    @output.setter
    def output(self, val):
        self.__output = []
        for x in range(0, len(val)):
            try:
                self.__output.append(__import__("rhasspy_weather.output." + val[x], fromlist=['']))
            except ImportError:
                pass
            self.__output[x].parse_config(self.__config_parser)
        if len(self.__output) == 0:
            raise ConfigError("No output found", "There is no module in the output folder that matches one of the output names in your config.")

    @property
    def output_template(self):
        return self.__output_template

    @output_template.setter
    def output_template(self, val):
        try:
            base_path = str(Path(__file__).parent.parent)
            self.__output_template = open(os.path.join(base_path, "output_templates", val), 'r').read()
        except OSError:
            raise ConfigError("No output template found", "There is no template that matches the name of your config.")

    @property
    def locale(self):
        return self.__locale

    @locale.setter
    def locale(self, val):
        try:
            self.__locale = __import__("rhasspy_weather.languages." + val, fromlist=[''])
        except ImportError:
            raise ConfigError("No locale found", "There is no module in the locale folder that matches the locale name in your config.")

    @property
    def location(self):
        return self.__location

    @location.setter
    def location(self, city: str, zipcode=None, country_code=None, lat=None, lon=None):
        self.__location = Location(city)
        if not ((lat is None or lon is None) or (lat == "" or lon == "")):
            self.location.set_lat_and_lon(lat, lon)
        if not (zipcode is None or country_code is None) or (zipcode is "" or country_code is ""):
            self.location.set_zipcode(zipcode, country_code)

    @staticmethod
    def __get_option_with_default_value(section: configparser.SectionProxy, option, default_value, data_type: str = ""):
        if section is not None and option in section:
            try:
                if data_type == "bool":
                    temp = section.getboolean(option)
                elif data_type == "int":
                    temp = section.getint(option)
                elif data_type == "float":
                    temp = section.getfloat(option)
                else:
                    temp = section.get(option)
                if option is None:
                    log.warning(f"Setting '{option}' is present but has no value. Please refer to 'config.default' for an example config.")
                    return default_value
                else:
                    return temp
            except ValueError:
                return default_value
        log.error(f"Setting '{option}' is missing from config. Please refer to 'config.default' for an example config.")
        return default_value


__config = None


def get_config():
    global __config
    global config_path
    if __config is None:
        rhasspy_weather_path = str(Path(__file__).parent.parent.parent)
        home_path = os.path.join(os.path.expanduser("~"), ".config", "rhasspy_weather")
        config_names = ["rhasspy_weather_config.ini", "config.ini", "rhasspy_weather.ini"]
        if os.path.exists(config_path):
            __config = WeatherConfig(config_path)
        else:
            log.warning(f"Config not found at '{config_path}'. Searching elsewhere.")
            for loc in rhasspy_weather_path, home_path:
                for config_name in config_names:
                    tmp_config_path = os.path.join(loc, config_name)
                    if os.path.exists(tmp_config_path):
                        config_path = tmp_config_path
                        __config = WeatherConfig(config_path)
        if __config is None:
            message = f"No config file found in '{rhasspy_weather_path}' or '{home_path}'. Please copy config.default into one of those paths and rename it to one of {str(config_names)}"
            raise ConfigError("No config found", message)
    return __config


def set_config_path(new_config_path: str):
    global config_path
    if os.path.exists(new_config_path):
        config_path = new_config_path
    else:
        log.warning(f"Config at {new_config_path} not found.")
