import configparser
import logging
import os
from pathlib import Path

import pytz

from rhasspy_weather.data_types.location import Location

log = logging.getLogger(__name__)

# TODO: implement custom config path and config names
# TODO: figure out what to do with config errors (if locale is working throw a WeatherError, else throw general config error maybe?)


class WeatherConfig:
    def __init__(self, config_path):
        log.info("Loading config")
        base_path = str(Path(__file__).parent.parent)
        # config_path = os.path.join(base_path, 'config.ini')
        # default_config_path = os.path.join(base_path, 'config.default')
        config_parser = configparser.ConfigParser(allow_no_value=True)
        self.__error = False
        config_parser.read(config_path)

        if not (config_parser.has_section("General") and config_parser.has_section("Location")):
            log.error("At least one required section is missing. Please refer to 'config.default' for an example config.")
            self.__error = True

        section_name_general = "General"
        if config_parser.has_section(section_name_general):
            section_general = config_parser[section_name_general]
            self.__units = self.__get_required_option(section_general, "units", "metric")
            api = self.__get_required_option(section_general, "api", "openweathermap")
            try:
                name = "rhasspy_weather.api." + api
                self.__api = __import__(name, fromlist=[''])
            except ImportError:
                log.error("There is no module in the api folder that matches the api name in your config.")
                self.__error = True
            parser = self.__get_required_option(section_general, "parser", "rhasspy_intent")
            try:
                name = "rhasspy_weather.parser." + parser
                self.__parser = __import__(name, fromlist=[''])
            except ImportError:
                log.error("There is no module in the parser folder that matches the parser name in your config.")
                self.__error = True

            output = self.__get_required_option(section_general, "output", "console_json")
            try:
                name = "rhasspy_weather.output." + output
                self.__output = __import__(name, fromlist=[''])
            except ImportError:
                log.error("There is no module in the output folder that matches the output name in your config.")
                self.__error = True

            output_template = self.__get_required_option(section_general, "output_template", "rhasspy.json")
            try:
                path = os.path.join(base_path, "output_templates", output_template)
                self.__output_template = open(path, 'r').read()
            except OSError:
                log.error("There is no template that matches the name of your config.")
                self.__error = True

            locale = self.__get_required_option(section_general, "locale", "german")
            try:
                name = "rhasspy_weather.languages." + locale
                self.__locale = __import__(name, fromlist=[''])
            except ImportError:
                log.error("There is no module in the locale folder that matches the locale name in your config.")
                self.__error = True
            self.__timezone = pytz.timezone(self.__get_required_option(section_general, "timezone", "Europe/Berlin"))

        else:
            log.error(f"Section [{section_name_general}] is missing from config. Please refer to 'config.default' for an example config.")
            self.__error = True

        section_name_weather = "Weather"
        if config_parser.has_section(section_name_weather):
            section_weather = config_parser[section_name_weather]
            self.__temp_warm_from = self.__get_required_option(section_weather, "temp_warm", 20, "int")
            self.__temp_cold_to = self.__get_required_option(section_weather, "temp_cold", 5, "int")
            self.__detail = self.__get_required_option(section_weather, "level_of_detail", False, "bool")
        else:
            log.error(f"Section [{section_name_general}] is missing from config. Please refer to 'config.default' for an example config.")
            self.__error = True

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
            log.error(f"Section [{section_name_location}] is missing from config. Please refer to 'config.default' for an example config.")
            self.__error = True

        if api == "openweathermap":
            section_name_openweathermap = "OpenWeatherMap"
            if config_parser.has_section(section_name_openweathermap):
                has_error = False
                section_openweathermap = config_parser[section_name_openweathermap]
                if "api_key" in section_openweathermap:
                    api_key = section_openweathermap.get("api_key")
                    if api_key is None:
                        self.__error = True
                    else:
                        self.__api_key = api_key
                else:
                    self.__error = True
                    has_error = True

                if has_error:
                    log.error("API is set to OpenWeatherMap yet no API-Key is found. Please refer to 'config.default' for an example config.")
            else:
                log.error("API is set to OpenWeatherMap yet no config section for that is found. Please refer to 'config.default' for an example config.")
                self.__error = True

        if "mqtt" in output:
            section_name_mqtt = "mqtt"
            if config_parser.has_section(section_name_mqtt):
                section_mqtt = config_parser[section_name_mqtt]
                self.__mqtt_address = self.__get_required_option(section_mqtt, "address", "")
                self.__mqtt_port = self.__get_required_option(section_mqtt, "port", 1883, "int")
                if self.__mqtt_address == "" or self.__mqtt_port == "":
                    log.error("You need to specify address and port for the mqtt output to work.")
                    self.__error = True
                self.__mqtt_user = section_mqtt.get("user")
                log.debug(section_mqtt.get("user"))
                self.__mqtt_password = section_mqtt.get("password")
                self.__mqtt_topic = self.__get_required_option(section_mqtt, "topic", "rhasspy_weather/response")

        if self.__error:
            log.error("Config Error")
        else:
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
    def output(self):
        return self.__output

    @property
    def output_template(self):
        return self.__output_template

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

    @property
    def mqtt_address(self):
        return self.__mqtt_address

    @property
    def mqtt_port(self):
        return self.__mqtt_port

    @property
    def mqtt_user(self):
        return self.__mqtt_user

    @property
    def mqtt_password(self):
        return self.__mqtt_password

    @property
    def mqtt_topic(self):
        return self.__mqtt_topic

    @property
    def error(self):
        return self.__error

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
                log.warning(f"Setting '{option}' is present but has no value. Please refer to 'config.default' for an example config.")
                return default_value
            else:
                return temp
        log.warning(f"Setting '{option}' is missing from config. Please refer to 'config.default' for an example config.")
        return default_value


__config = None


def get_config():
    global __config
    if __config is None:
        rhasspy_weather_path = str(Path(__file__).parent.parent.parent)
        home_path = os.path.join(os.path.expanduser("~"), ".config", "rhasspy_weather")
        config_name = "rhasspy_weather_config.ini"
        default_config_path = os.path.join(rhasspy_weather_path, 'config.default')
        for loc in rhasspy_weather_path, home_path:
            config_path = os.path.join(loc, config_name)
            if os.path.exists(config_path):
                __config = WeatherConfig(config_path)
        if __config is None:
            raise Exception(f"No config file found in {rhasspy_weather_path} or {home_path}. Please copy \
                            config.default into one of those paths and rename it to {config_name}")
    return __config
