# -*- encoding: utf-8 -*-
import datetime
import locale
from rhasspy_weather.weather_logic import WeatherRequest, DateType, ForecastType, WeatherForecast, WeatherReport, Location, Grain
import copy

class Weather:
    def __init__(self):
        self.detail = False
        self.weather_api_key = "eb22adf9da71420af7da325084003385"
        self.location = Location("Frankfurt")
        zipcode = "60389"
        country = "de"
        self.location.set_zipcode(zipcode, country)
        self.units = "metric"
        # try:
            # locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
        # except locale.Error:
            # print("That locale doesn't exist on the system")

    # function being called when snips detects an intent related to the weather
    def get_weather_forecast(self, intent_message):
        #print("function: get_weather_forecast")
        requests = self.parse_intent_message(intent_message)
        response = ""
        #print(*requests, sep='\n')
        for request in requests:
            if request.location == "":
                forecast = WeatherForecast(self.units, self.location)
            else:
                forecast = WeatherForecast(self.units, Location(request.location))
            forecast.get_weather_from_open_weather_map(self.weather_api_key)
            response = response + WeatherReport(request, forecast).generate_report()
        
        return response

    # parse the query and return a list of WeatherRequests
    def parse_intent_message(self, intent_message):
        #print("function: parse_intent_message")
        requests = []
        #intent
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
        
        # if a day was specified
        if intent_message["slots"]["when_day"] != "":
            # is it today, tomorrow or the day after tomorrow (day in date_offset)?
            if intent_message["slots"]["when_day"] in date_offset:
                new_request.request_date = datetime.date.today() + datetime.timedelta(date_offset.index(intent_message["slots"]["when_day"]))
                new_request.date_specified += intent_message["slots"]["when_day"]
            # is a weekday named?
            elif intent_message["slots"]["when_day"] in days:
                today = datetime.date.today();
                for x in range(7):
                    new_date = today + datetime.timedelta(x)
                    if intent_message["slots"]["when_day"] == days[new_date.weekday()]:
                        new_request.request_date = new_date
                        new_request.date_specified += "am " + intent_message["slots"]["when_day"]
                        break
            # was a date specified (specified by rhasspy as "daynumber monthname")?
            elif ' ' in intent_message["slots"]["when_day"]:
                day, month = intent_message["slots"]["when_day"].split()
                new_request.date_specified += "am " + day + ". " + month
                # won't work when the year changes, fix that sometime
                try:
                    new_request.request_date = datetime.date(datetime.date.today().year, months.index(month)+1, int(day))
                except ValueError:
                    new_request.request_date = -1
            
            # if a time was specified
            if "when_time" in intent_message["slots"] and intent_message["slots"]["when_time"] != "":
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
        requested = None
        if intent == ForecastType.CONDITION:
            requested = intent_message["slots"]["condition"]
        elif intent == ForecastType.ITEM:
            requested = intent_message["slots"]["item"]
        elif intent == ForecastType.TEMPERATURE:
            requested = intent_message["slots"]["temperature"]
        new_request.requested = requested.capitalize() # first letter uppercase because german nouns just are that way (and the weather_logic will break)
        
        requests.append(new_request)

        # location
        # locations = intent_message.slots.forecast_locality.all()
        # if locations is not None and len(locations) > 0:
            # tmp_requests = copy.copy(requests)
            # for request in tmp_requests:
                # requests.remove(request)
                # for locality in locations:
                    # new_request = copy.deepcopy(request)
                    # new_request.location = locality.value
                    # requests.append(new_request)

       
        
                    
        return requests