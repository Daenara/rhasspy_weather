import datetime
from rhasspy_weather.data_types.request import WeatherRequest, DateType, ForecastType, Grain
from rhasspy_weather.data_types.status import Status, StatusCode
from rhasspy_weather.data_types.location import Location

import logging

log = logging.getLogger(__name__)

def parse_intent_message(intent_message, config):
    intent = None
    
    # if you changed the slot names in rhasspy, change them here, too
    slot_day_name = "when_day"
    slot_time_name = "when_time"
    slot_location_name = "location"
    slot_item_name = "item"
    slot_condition_name = "condition"
    slot_temperature_name = "temperature"
    
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
    slots = intent_message["slots"]
    if slot_day_name in slots and slots[slot_day_name] != "":
        log.debug("it was a day specified")
        # is it today, tomorrow or the day after tomorrow (day in date_offset)?
        if slots[slot_day_name] in date_offset:
            log.debug("    day offset detected")
            new_request.request_date = datetime.date.today() + datetime.timedelta(date_offset.index(slots[slot_day_name]))
            new_request.date_specified = slots[slot_day_name]
        # is a weekday named?
        elif slots[slot_day_name] in days:
            log.debug("    weekday detected")
            for x in range(7):
                new_date = today + datetime.timedelta(x)
                if slots[slot_day_name] == days[new_date.weekday()]:
                    new_request.request_date = new_date
                    new_request.date_specified = "am " + slots[slot_day_name]
                    break
        # was a date specified (specified by rhasspy as "daynumber monthname")?
        elif ' ' in slots[slot_day_name]:
            log.debug("    date detected")
            day, month = slots[slot_day_name].split()
            new_request.date_specified = "am " + day + ". " + month
            # won't work when the year changes, fix that sometime
            try:
                new_request.request_date = datetime.date(datetime.date.today().year, months.index(month)+1, int(day))
            except ValueError:
                new_request.status.set_status(StatusCode.DATE_ERROR)
        
        # if a time was specified
        if slot_time_name in slots and slots[slot_time_name] != "":
            log.debug("it was a time specified")
            new_request.grain = Grain.HOUR
            # was something like midday specified (listed in time_range)?
            if slots[slot_time_name] in time_range:
                log.debug("    named time frame detected")
                new_request.date_type = DateType.INTERVAL
                new_request.start_time = time_range[slots[slot_time_name]][0]
                new_request.end_time = time_range[slots[slot_time_name]][1]
                new_request.time_specified = slots[slot_time_name]
            # was it hours and minutes (specified as "HH MM" by rhasspy intent)?
            elif isinstance(slots[slot_time_name], str) and ' ' in slots[slot_time_name]:
                log.debug("    hours and minutes detected")
                new_request.start_time = datetime.datetime.strptime(slots[slot_time_name], '%H %M').time()
            # is it only an hour (no way to only specify minutes, if it is an int, it is hours)?
            elif isinstance(slots[slot_time_name], int):
                log.debug("    hours detected")
                new_request.start_time = datetime.time(slots[slot_time_name], 0)
        else:
            log.debug("no time specified, getting weather for the full day")
    else:
        log.debug("no day specified, using today as default")
    
    # requested
    requested = None
    if intent == ForecastType.CONDITION and slot_condition_name in slots:
        requested = slots[slot_condition_name]
    elif intent == ForecastType.ITEM and slot_item_name in slots:
        requested = slots[slot_item_name]
    elif intent == ForecastType.TEMPERATURE and slot_temperature_name in slots:
        requested = slots[slot_temperature_name]
    if not requested == None:
        log.debug("there was a special request made")
        new_request.requested = requested.capitalize() # first letter uppercase because german nouns just are that way (and the weather_logic will break)

    # location
    if slot_location_name in slots:
        log.debug("a location was specified")
        new_request.location = Location(slots[slot_location_name])
                
    return new_request