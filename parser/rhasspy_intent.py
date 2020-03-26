import datetime
from rhasspy_weather.data_types.request import WeatherRequest, DateType, ForecastType, Grain
from rhasspy_weather.data_types.status import Status, StatusCode
from rhasspy_weather.data_types.location import Location

import logging

log = logging.getLogger(__name__)

def parse_intent_message(intent_message, config):
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
    today = datetime.datetime.now(config.timezone).date()
    #define default request
    new_request = WeatherRequest(DateType.FIXED, Grain.DAY, today, intent, config)

    # if a day was specified
    if "when_day" in intent_message["slots"] and intent_message["slots"]["when_day"] != "":
        log.debug("it was a day specified")
        # is it today, tomorrow or the day after tomorrow (day in date_offset)?
        if intent_message["slots"]["when_day"] in date_offset:
            log.debug("    day offset detected")
            new_request.request_date = datetime.date.today() + datetime.timedelta(date_offset.index(intent_message["slots"]["when_day"]))
            new_request.date_specified += intent_message["slots"]["when_day"]
        # is a weekday named?
        elif intent_message["slots"]["when_day"] in days:
            log.debug("    weekday detected")
            for x in range(7):
                new_date = today + datetime.timedelta(x)
                if intent_message["slots"]["when_day"] == days[new_date.weekday()]:
                    new_request.request_date = new_date
                    new_request.date_specified += "am " + intent_message["slots"]["when_day"]
                    break
        # was a date specified (specified by rhasspy as "daynumber monthname")?
        elif ' ' in intent_message["slots"]["when_day"]:
            log.debug("    date detected")
            day, month = intent_message["slots"]["when_day"].split()
            new_request.date_specified = "am " + day + ". " + month
            # won't work when the year changes, fix that sometime
            try:
                new_request.request_date = datetime.date(datetime.date.today().year, months.index(month)+1, int(day))
            except ValueError:
                new_request.status.set_status(StatusCode.DATE_ERROR)
        
        # if a time was specified
        if "when_time" in intent_message["slots"] and intent_message["slots"]["when_time"] != "":
            log.debug("it was a time specified")
            new_request.grain = Grain.HOUR
            # was something like midday specified (listed in time_range)?
            if intent_message["slots"]["when_time"] in time_range:
                log.debug("    named time frame detected")
                new_request.date_type = DateType.INTERVAL
                new_request.start_time = time_range[intent_message["slots"]["when_time"]][0]
                new_request.end_time = time_range[intent_message["slots"]["when_time"]][1]
                new_request.time_specified += intent_message["slots"]["when_time"]
            # was it hours and minutes (specified as "HH MM" by rhasspy intent)?
            elif isinstance(intent_message["slots"]["when_time"], str) and ' ' in intent_message["slots"]["when_time"]:
                log.debug("    hours and minutes detected")
                new_request.start_time = datetime.datetime.strptime(intent_message["slots"]["when_time"], '%H %M').time()
            # is it only an hour (no way to only specify minutes, if it is an int, it is hours)?
            elif isinstance(intent_message["slots"]["when_time"], int):
                log.debug("    hours detected")
                new_request.start_time = datetime.time(intent_message["slots"]["when_time"], 0)
        else:
            log.debug("no time specified, getting weather for the full day")
    else:
        log.debug("no day specified, using today as default")
    
    # requested
    requested = None
    if intent == ForecastType.CONDITION and "condition" in intent_message["slots"]:
        requested = intent_message["slots"]["condition"]
    elif intent == ForecastType.ITEM and "item" in intent_message["slots"]:
        requested = intent_message["slots"]["item"]
    elif intent == ForecastType.TEMPERATURE and "temperature" in intent_message["slots"]:
        requested = intent_message["slots"]["temperature"]
    if not requested == None:
        log.debug("there was a special request made")
        new_request.requested = requested.capitalize() # first letter uppercase because german nouns just are that way (and the weather_logic will break)

    # location
    if "location" in intent_message["slots"]:
        log.debug("a location was specified")
        new_request.location = Location(intent_message["slots"]["location"])
                
    return new_request