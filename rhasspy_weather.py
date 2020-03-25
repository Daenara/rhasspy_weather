# -*- encoding: utf-8 -*-
import datetime
from rhasspy_weather.helpers import DateType, ForecastType, Location, Grain
from rhasspy_weather.openweathermap import get_weather
from rhasspy_weather.forecast import WeatherForecast
from rhasspy_weather.request import WeatherRequest
from rhasspy_weather.report import WeatherReport
from rhasspy_weather.status import Status, StatusCode
import copy
import configparser
import shutil
import os
import logging

log = logging.getLogger(__name__)

class Weather:
    def __init__(self):
        self.status = Status()
        try:
            base_path = os.path.dirname(__file__)
            config_path = os.path.join(base_path, 'config.ini')
            default_config_path = os.path.join(base_path, 'config.default')
            config = configparser.ConfigParser()
            if not os.path.isfile(config_path):
                log.info("No config found, creating config")
                shutil.copy(default_config_path, config_path)
            config.read(config_path)
            self.detail = config['General'].getboolean('LevelOfDetail', False)
            self.weather_api_key = config['OpenWeatherMap'].get('api_key')
            self.location = Location(config['Location'].get('City', "Berlin"))
            self.location.set_zipcode(config['Location'].get('Zipcode'), config['Location'].get('CountryCode'))
            self.units = config['General'].get('Units', "metric")
            log.info("Config Loaded")
        except:
            self.status.set_status(StatusCode.CONFIG_ERROR)

    # function being called when snips detects an intent related to the weather
    def get_weather_forecast(self, intent_message):
        log.info("Checking for previous errors")
        if self.status.is_error:
            return self.status.status_response()
        
        log.info("Parsing rhasspy intent")
        request = self.parse_intent_message(intent_message)
        if request.status.is_error:
            return request.status.status_response()
        
        log.info("Requesting weather")
        forecast = get_weather(self.weather_api_key, request.location, self.units)
        if forecast.status.is_error:
            return forecast.status.status_response()
        
        log.info("Formulating answer")
        response = WeatherReport(request, forecast).generate_report()
        
        return response

    # parse the query and return a list of WeatherRequests
    def parse_intent_message(self, intent_message):
        intent = None
        
        if "GetWeatherForecastCondition" == intent_message["intent"]["name"]:
            intent = ForecastType.CONDITION
        elif "GetWeatherForecastItem" == intent_message["intent"]["name"]:
            intent = ForecastType.ITEM
        elif "GetWeatherForecastTemperature" == intent_message["intent"]["name"]:
            intent = ForecastType.TEMPERATURE
        elif  "GetWeatherForecast" == intent_message["intent"]["name"]:
            intent = ForecastType.FULL
        
        # date and time
        days = ["montag","dienstag","mittwoch","donnerstag","freitag","samstag","sonntag"]
        months = ["januar", "februar", "märz", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "dezember"]
        date_offset = ["heute", "morgen", "übermorgen"]
        time_range = {"morgen": (datetime.time(6, 0), datetime.time(10, 0)),"vormittag": (datetime.time(10, 0), datetime.time(12, 0)), "mittag": (datetime.time(12, 0), datetime.time(14, 0)), "nachmittag": (datetime.time(15, 0), datetime.time(18, 0)), "abend": (datetime.time(18, 0), datetime.time(22, 0)), "nacht": (datetime.time(22, 0), datetime.time(7, 0))}
        
        #define default request
        new_request = WeatherRequest(DateType.FIXED, Grain.DAY, datetime.date.today(), intent, self.detail)

        log.debug(new_request)
        # if a day was specified
        if intent_message["slots"]["when_day"] != "":
            log.debug("day specified")
            log.debug(intent_message["slots"]["when_day"])
            # is it today, tomorrow or the day after tomorrow (day in date_offset)?
            if intent_message["slots"]["when_day"] in date_offset:
                log.debug("day offset")
                new_request.request_date = datetime.date.today() + datetime.timedelta(date_offset.index(intent_message["slots"]["when_day"]))
                new_request.date_specified += intent_message["slots"]["when_day"]
            # is a weekday named?
            elif intent_message["slots"]["when_day"] in days:
                log.debug("weekday")
                today = datetime.date.today();
                for x in range(7):
                    new_date = today + datetime.timedelta(x)
                    if intent_message["slots"]["when_day"] == days[new_date.weekday()]:
                        new_request.request_date = new_date
                        new_request.date_specified += "am " + intent_message["slots"]["when_day"]
                        break
            # was a date specified (specified by rhasspy as "daynumber monthname")?
            elif ' ' in intent_message["slots"]["when_day"]:
                log.debug("date")
                day, month = intent_message["slots"]["when_day"].split()
                new_request.date_specified = "am " + day + ". " + month
                # won't work when the year changes, fix that sometime
                try:
                    new_request.request_date = datetime.date(datetime.date.today().year, months.index(month)+1, int(day))
                except ValueError:
                    new_request.status.set_status(StatusCode.DATE_ERROR)
            
            # if a time was specified
            if "when_time" in intent_message["slots"] and intent_message["slots"]["when_time"] != "":
                log.debug("time specified")
                new_request.grain = Grain.HOUR
                # was something like midday specified (listed in time_range)?
                if intent_message["slots"]["when_time"] in time_range:
                    new_request.date_type = DateType.INTERVAL
                    new_request.start_time = time_range[intent_message["slots"]["when_time"]][0]
                    new_request.end_time = time_range[intent_message["slots"]["when_time"]][1]
                    new_request.time_specified += intent_message["slots"]["when_time"]
                # was it hours and minutes (specified as "HH MM" by rhasspy intent)?
                elif isinstance(intent_message["slots"]["when_time"], str) and ' ' in intent_message["slots"]["when_time"]:
                    new_request.start_time = datetime.datetime.strptime(intent_message["slots"]["when_time"], '%H %M').time()
                # is it only an hour (no way to only specify minutes, if it is an int, it is hours)?
                elif isinstance(intent_message["slots"]["when_time"], int):
                    new_request.start_time = datetime.time(intent_message["slots"]["when_time"], 0)
        
        # requested
        log.debug("figuring out special requests")
        requested = None
        log.debug(intent)
        log.debug(requested)
        if intent == ForecastType.CONDITION and "condition" in intent_message["slots"]:
            requested = intent_message["slots"]["condition"]
        elif intent == ForecastType.ITEM and "item" in intent_message["slots"]:
            requested = intent_message["slots"]["item"]
        elif intent == ForecastType.TEMPERATURE and "temperature" in intent_message["slots"]:
            requested = intent_message["slots"]["temperature"]
        if not requested == None:
            new_request.requested = requested.capitalize() # first letter uppercase because german nouns just are that way (and the weather_logic will break)

        # location
        if "location" in intent_message["slots"]:
            new_request.location = Location(intent_message["slots"]["location"])
            new_request.location_specified = True
        else:
            new_request.location = self.location
                    
        return new_request