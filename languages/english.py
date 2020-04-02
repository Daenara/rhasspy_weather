import datetime

from rhasspy_weather.data_types.condition import ConditionType
from rhasspy_weather.data_types.status import StatusCode

# general stuff
temperature_warm_from = 20  # TODO: discuss, this should go into the config.ini - values don't make sense for example in Brazil 
temperature_cold_to = 5

# used in parsers
weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
named_days = {"today": 0, "tomorrow": 1, "the day after tomorrow": 2}
named_times = {
    "morning": (datetime.time(6, 0), datetime.time(12, 0)),
    "midday": datetime.time(12, 0),
    "afternoon": (datetime.time(12, 0), datetime.time(18, 0)),
    "evening": (datetime.time(18, 0), datetime.time(22, 0)),
    "night": (datetime.time(22, 0), datetime.time(6, 0)),
    "midnight": datetime.time(23, 59)
}
named_times_synonyms = {
    "noon": "midday",
}
requested_condition = {
    "rain": ConditionType.RAIN,
    "snow": ConditionType.SNOW,
    "mist": ConditionType.MIST,
    "fog": ConditionType.MIST, # TODO: what about haze, hazy, misty, foggy?
    "clouds": ConditionType.CLOUDS, # TODO: cloudy?
    "thunderstorm": ConditionType.THUNDERSTORM,
    "sun": ConditionType.CLEAR,
    "wind": ConditionType.WIND # TODO: windy, stormy
}
requested_temperature = {
    "warm": "warm",
    "cold": "cold"
}


def format_userdefined_date(date):
    return "on " + date


def format_userdefined_time(hour, minutes=""):
    if minutes == "":
        return "at {} o'clock {}m".format(hour%12, "a" if hour < 12 else "p")
    return "at {} {:02d}".format(hour, minutes)


# used in status.py to output status messages
status_response = {
    StatusCode.NORMAL: ["Everything seems to be okay."],
    StatusCode.NO_NETWORK_ERROR: ["I don't have network.", 
        "I seem not be connected to the internet."],
    StatusCode.API_ERROR: ["There is a problem with the API Key.", 
        "the API key is invalid."],
    StatusCode.FUTURE_WEATHER_ERROR: ["I don't know the weather this far ahead.",
        "There is not prediction data for your requested date yet."],
    StatusCode.NOT_IMPLEMENTED_ERROR: ["This function is not implemented."],
    StatusCode.LOCATION_ERROR: ["I can't find the location."],
    StatusCode.PAST_WEATHER_ERROR: ["I don't know the weather of the past.",
    "I am a forecasting service not a historian."],
    StatusCode.NO_WEATHER_FOR_DAY_ERROR: ["There seems to be no weather for today."],
    StatusCode.DATE_ERROR: ["Something is wrong with the date."],
    StatusCode.API_TIMEOUT_ERROR: ["API Key was used to often, try again later."],
    StatusCode.CONFIG_ERROR: ["There seems to be something wrong with the configuration file."],
    StatusCode.TIME_ERROR: ["Something is wrong with the time."],
    StatusCode.GENERAL_ERROR: ["Something went wrong."]
}


# used in report.py

def format_output_location(location):
    return "in {0}".format(location.capitalize())


def format_output_date(request):
    date = "on " + request.readable_date

    if request.time_difference == 0:
        date = "today"
    elif request.time_difference == 1:
        date = "tomorrow"
    else:
        temp_day = datetime.datetime.today().weekday() + request.time_difference
        if temp_day < 7:
            date = "on " + request.weekday
        elif temp_day < 14:
            date = request.weekday + " next week"
    return date


def format_output_time(request):
    return "at " + request.readable_start_time + " o'clock"


# temperature report

temperature_answers = {
    "cold_true": ["Yes, it will be cold {where} {when}. The temperature will be {temperature}."],
    "cold_false": ["No, {when} {where} will not be cold. The temperature will be {temperature}."],
    "warm_true": ["Yes, it will be warm {where} {when}. The temperature will be {temperature}."],
    "warm_false": ["No, {when} {where} will not be warm. The temperature will be {temperature}."],
    "general_temperature": ["The temperature {when} {where} is {temperature}."]
}


def format_temperature_output(min_temperature, max_temperature):
    if min_temperature == max_temperature:
        return str(min_temperature) + " degrees"  # TODO: add Celsius/centigrade?
    else:
        return "between " + str(min_temperature) + " and " + str(max_temperature) + " degrees"


# condition report

condition_answers = {
    "general_weather": ["The weather {when} {where}: {weather}."],
    "rain_true": ["Yes, {when} could be rainy {where}."],
    "rain_false": ["No, it will not rain {when} {where}. The weather will be: {weather}."],
    "snow_true": ["Yes, {when} {where} might have snow."],
    "snow_false": ["No, there will be no snow {when} {where}. The weather will be: {weather}."],
    "thunderstorm_true": ["Yes, {when} could have a thunderstorm {where}."],
    "thunderstorm_false": ["I don't know about a thunderstorm {when} {where}. The weather will be: {weather}."],
    "clouds_true": ["Yes, {when} {where} could be cloudy."],
    "clouds_false": ["No, {when} {where} will not be cloudy. The weather will be: {weather}."],
    "sun_true": ["Yes, {when} {where} will be sunny."],
    "sun_false": ["No, {when} {where} won't have a clear sky. The weather will be: {weather}."],
    "mist_true": ["Yes, {when} {where} might be foggy."],
    "mist_false": ["No, {when} {where} will have no fog. The weather will be: {weather}."],
    "unknown_condition": ["I don't know what you want to know. Here the general weather: {weather}"]
}


def combine_conditions(conditions):
    if isinstance(conditions, list):
        if len(conditions) == 0:
            return ""
        elif len(conditions) == 1:
            return conditions[0]
        else:
            combined = conditions[0]
            for x in conditions[1:-1]:
                combined += ", " + x
            combined += " and " + conditions[-1]
            return combined


# items
rain_items = ["umbrella", "raincoat", "rubber boots"]
warm_items = ["sunglasses", "sunscreen", "sandals"]
cold_items = ["boots", "scarf", "gloves"]

item_answers = {
    "rain": ["It could be rainy {when} {where}. Taking {item} might be a good idea."],
    "no_rain": ["There should be no rain {when} {where}. {item} is probably not necessary.",
        "No, you will most likely not need {item}. No rain is expected {when} {where}."],
    "warm_and_sunny": ["It will be warm {when} {where} and the sun might come out during the day. {item} might be a good idea."],
    "not_warm_and_sunny": ["It will not exactly be warm {when} {where} but it might still be sunny. {item} could still be useful."],
    "not_sunny": ["It will not be sunny {when} {where}. {item} might be necessary."],
    "cold": ["It will be cold {when} {where}. {item} might be a good idea."],
    "not_cold": ["It will not be cold {when} {where}, so {item} might not help."],
    "unknown_item": ["I have no idea what {item} is, I am sorry."]
}


def format_item_for_output(item):
    if item in ["umbrella"]:
        return "an " + item
    elif item in ["boots", "sunglasses"]:
        return item
    elif item in ["scarf", "raincoat"]:
        return "a " + item
    elif item in ["sunscreen"]:
        return item
    else:
        return item
