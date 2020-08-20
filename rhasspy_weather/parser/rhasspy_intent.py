import datetime
import logging

from rhasspy_weather import utils
from rhasspy_weather.data_types.condition import ConditionType
from rhasspy_weather.data_types.location import Location
from rhasspy_weather.data_types.request import WeatherRequest, DateType, ForecastType, Grain
from rhasspy_weather.data_types.config import get_config

log = logging.getLogger(__name__)

# TODO: split into smaller sections to make testing easier (and try to make it easier to read/use while at it)
# if you changed the slot names in rhasspy, change them here on the right side
slot_names = {
    "day": "when_day",
    "time": "when_time",
    "location": "location",
    "item": "item",
    "condition": "condition",
    "temperature": "temperature"
}


def parse_intent_message(intent_message):
    intent = None

    config = get_config()

    if "GetWeatherForecastCondition" == intent_message["intent"]["name"]:
        intent = ForecastType.CONDITION
    elif "GetWeatherForecastItem" == intent_message["intent"]["name"]:
        intent = ForecastType.ITEM
    elif "GetWeatherForecastTemperature" == intent_message["intent"]["name"]:
        intent = ForecastType.TEMPERATURE
    elif "GetWeatherForecast" == intent_message["intent"]["name"]:
        intent = ForecastType.FULL

    today = datetime.datetime.now(config.timezone).date()

    # define default request
    new_request = WeatherRequest(DateType.FIXED, Grain.DAY, today, intent)

    # if a day was specified
    slots = intent_message["slots"]
    if slot_names["day"] in slots and slots[slot_names["day"]] != "":
        log.debug("it was a day specified")
        named_days_lowercase = [x.lower() for x in config.locale.named_days]
        weekdays_lowercase = [x.lower() for x in config.locale.weekday_names]
        named_days_synonyms_lowercase = [x.lower() for x in config.locale.named_times_synonyms]
        named_days_combined = named_days_lowercase + named_days_synonyms_lowercase
        # is it a named day (tomorrow, etc.)?
        if slots[slot_names["day"]].lower() in named_days_combined:
            log.debug("  named day detected")
            if slots[slot_names["day"]].lower() in named_days_synonyms_lowercase:
                index = named_days_synonyms_lowercase.index(slots[slot_names["day"]].lower())
                name = list(config.locale.named_days_synonyms.keys())[index]
                value = config.locale.named_days[config.locale.named_days_synonyms[name]]
            else:
                index = named_days_lowercase.index(slots[slot_names["day"]].lower())
                name = list(config.locale.named_days.keys())[index]
                value = list(config.locale.named_days.values())[index]
            if isinstance(value, datetime.date):
                log.debug("    named day seems to be a date")
                new_request.request_date = value
                new_request.date_specified = name
            elif isinstance(value, int):
                log.debug("    named day seems to be an offset from today")
                new_request.request_date = datetime.date.today() + datetime.timedelta(value)
                new_request.date_specified = name
        # is a weekday named?
        elif slots[slot_names["day"]].lower() in weekdays_lowercase:
            log.debug("  weekday detected")
            index = weekdays_lowercase.index(slots[slot_names["day"]].lower())
            name = config.locale.weekday_names[index]
            for x in range(7):
                new_date = today + datetime.timedelta(x)
                if slots[slot_names["day"]].lower() == weekdays_lowercase[new_date.weekday()]:
                    new_request.request_date = new_date
                    new_request.date_specified = config.locale.format_userdefined_date(name)
                    break
        # was a date specified (specified by rhasspy as "daynumber monthname")?
        elif ' ' in slots[slot_names["day"]]:
            log.debug("  date detected")
            day, month = slots[slot_names["day"]].split()
            months_lowercase = [x.lower() for x in config.locale.month_names]
            if month.lower() in months_lowercase:
                index = months_lowercase.index(month.lower())
                name = config.locale.month_names[index]
                new_request.date_specified = config.locale.format_userdefined_date(day + ". " + name)
                new_request.request_date = utils.get_date_with_year(int(day), index + 1)

        # if a time was specified
        if slot_names["time"] in slots and slots[slot_names["time"]] != "":
            log.debug("it was a time specified")
            new_request.grain = Grain.HOUR

            named_times_lowercase = [x.lower() for x in config.locale.named_times]
            named_times_synonyms_lowercase = [x.lower() for x in config.locale.named_times_synonyms]
            named_times_combined = named_times_lowercase + named_times_synonyms_lowercase
            # was something like midday specified (listed in locale.named_times or in locale.named_times_synonyms)?
            if isinstance(slots[slot_names["time"]], str) and slots[slot_names["time"]].lower() in named_times_combined:
                log.debug("  named time frame detected")
                if slots[slot_names["time"]].lower() in named_times_synonyms_lowercase:
                    index = named_times_synonyms_lowercase.index(slots[slot_names["time"]].lower())
                    name = list(config.locale.named_times_synonyms.keys())[index]
                    value = config.locale.named_times[config.locale.named_times_synonyms[name]]
                else:
                    index = named_times_lowercase.index(slots[slot_names["time"]].lower())
                    name = list(config.locale.named_times.keys())[index]
                    value = list(config.locale.named_times.values())[index]
                log.debug(value)
                if isinstance(value, datetime.time):
                    log.debug("    named time seems to be a certain time")
                    new_request.start_time = value
                    new_request.time_specified = name
                elif isinstance(value, tuple):
                    log.debug("    named time seems to be an interval")
                    new_request.date_type = DateType.INTERVAL
                    new_request.start_time = value[0]
                    new_request.end_time = value[1]
                    new_request.time_specified = name
            # was it hours and minutes (specified as "HH MM" by rhasspy intent)?
            elif isinstance(slots[slot_names["time"]], str) and ' ' in slots[slot_names["time"]]:
                log.debug("    hours and minutes detected")
                new_request.start_time = datetime.datetime.strptime(slots[slot_names["time"]], '%H %M').time()
                new_request.time_specified = config.locale.format_userdefined_time(new_request.start_time.hour,
                                                                                   new_request.start_time.minute)
            # is it only an hour (no way to only specify minutes, if it is an int, it is hours)?
            elif isinstance(slots[slot_names["time"]], int):
                log.debug("    hours detected")
                new_request.start_time = datetime.time(slots[slot_names["time"]], 0)
                new_request.time_specified = config.locale.format_userdefined_time(new_request.start_time.hour)
            else:
                new_request.grain = Grain.DAY
        else:
            log.debug("no time specified, getting weather for the full day")
    else:
        log.debug("no day specified, using today as default")

    # requested
    requested = None
    if intent == ForecastType.CONDITION and slot_names["condition"] in slots:
        if slots[slot_names["condition"]] in config.locale.condition_types:
            requested = config.locale.condition_types[slots[slot_names["condition"]]]
        elif slots[slot_names["condition"]] in config.locale.condition_synonyms:
            requested = config.locale.condition_types[config.locale.condition_synonyms[slots[slot_names["condition"]]]]
        else:
            requested = ConditionType.UNKNOWN
    elif intent == ForecastType.ITEM and slot_names["item"] in slots:
        items = config.locale.rain_items + config.locale.cold_items + config.locale.warm_items + config.locale.sun_items
        items_lowercase = [x.lower() for x in items]
        if slots[slot_names["item"]].lower() in items_lowercase:
            requested = items[items_lowercase.index(slots[slot_names["item"]].lower())]
    elif intent == ForecastType.TEMPERATURE and slot_names["temperature"] in slots:
        if slots[slot_names["temperature"]] in config.locale.temperature_types:
            requested = config.locale.temperature_types[slots[slot_names["temperature"]]]
        elif slots[slot_names["temperature"]] in config.locale.temperature_synonyms:
            requested = config.locale.temperature_types[
                config.locale.temperature_synonyms[slots[slot_names["temperature"]]]]
    if requested is not None:
        log.debug("there was a special request made")
        new_request.requested = requested

    # location
    if slot_names["location"] in slots and slots[slot_names["location"]] != "":
        log.debug("a location was specified")
        new_request.location = Location(slots[slot_names["location"]])

    return new_request
