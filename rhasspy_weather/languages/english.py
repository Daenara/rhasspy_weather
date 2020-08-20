import datetime

from rhasspy_weather.utils import utils
from rhasspy_weather.data_types.condition import ConditionType
from rhasspy_weather.data_types.item_list import WeatherItemList
from rhasspy_weather.data_types.error import ErrorCode

# general stuff
from rhasspy_weather.data_types.fixed_times import FixedTimes
from rhasspy_weather.data_types.temperature import TemperatureType

language_code = "en"

# used in parsers
weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
               "November", "December"]
named_days = {"today": 0, "tomorrow": 1, "the day after tomorrow": 2}
named_days_synonyms = {}
named_times = {
    "morning": (datetime.time(6, 0), datetime.time(12, 0)),
    "midday": datetime.time(12, 0),
    "afternoon": (datetime.time(12, 0), datetime.time(18, 0)),
    "evening": (datetime.time(18, 0), datetime.time(22, 0)),
    "night": (datetime.time(22, 0), datetime.time(6, 0)),
    "midnight": datetime.time(23, 59),
    "now": datetime.datetime.now().time(),  # somehow put timezone in here without producing a loop with the config
}
named_times_synonyms = {
    "noon": "midday",
    "tonight": "night",
    "currently": "now",
    "right now": "now",
    "at the moment": "now",
    "early morning": "morning"
}
condition_types = {
    "rain": ConditionType.RAIN,
    "snow": ConditionType.SNOW,
    "mist": ConditionType.MIST,
    "fog": ConditionType.MIST,
    "clouds": ConditionType.CLOUDS,
    "thunderstorm": ConditionType.THUNDERSTORM,
    "sun": ConditionType.SUN,
    "stars": ConditionType.STARS,
    "clear": ConditionType.CLEAR,
    "wind": ConditionType.WIND
}
condition_synonyms = {
    "rainy": "rain",
    "raining": "rain",
    "snowy": "snow",
    "snowing": "snow",
    "foggy": "fog",
    "misty": "mist",
    "cloudy": "clouds",
    "thunderstorms": "thunderstorm",
    "thunder": "thunderstorm",
    "lightning": "thunderstorm",
    "sun shine": "sun",
    "sunny": "sun",
    "windy": "wind",
    "storming": "wind",
    "stormy": "wind",
    "clear sky": "clear"
}
temperature_types = {
    "warm": TemperatureType.WARM,
    "cold": TemperatureType.COLD,
}
temperature_synonyms = {
    "freezing": "cold",
    "hot": "warm",
    "cool": "cold"
}


def format_userdefined_date(date):
    return "on " + date


def format_userdefined_time(hour, minutes=-1):
    if minutes == -1:
        return "at {} o'clock {}m".format(hour % 12, "a" if hour < 12 else "p")
    return "at {} {:02d}".format(hour, minutes)


# weather conditions

conditions = {
    ConditionType.WIND: {0: "calm", 1: "Light air", 2: "Light breeze", 3: "Gentle breeze", 4: "Moderate breeze",
                         5: "Fresh breeze", 6: "Strong breeze", 7: "High wind", 8: "Gale",
                         9: "Strong gale", 10: "storm", 11: "Violent storm", 12: "Hurricane force"},
    ConditionType.CLOUDS: {0: "clear sky", 1: "a few clouds", 2: "scattered clouds", 3: "broken clouds",
                           4: "overcast clouds"},
    ConditionType.RAIN: {0: "light rain", 1: "moderate rain", 2: "heavy rain", 3: "very heavy rain", 4: "extreme rain"},
    ConditionType.SNOW: {0: "light snow", 1: "snow", 2: "heavy snow"},
    ConditionType.THUNDERSTORM: {0: "light thunderstorm", 1: "thunderstorm", 2: "strong thunderstorm"}}

# used in error.py to output status messages
status_response = {
    ErrorCode.NO_NETWORK_ERROR: ["I don't have network.",
                                  "I seem not be connected to the internet."],
    ErrorCode.API_ERROR: ["There is a problem with the API Key.",
                           "the API key is invalid."],
    ErrorCode.FUTURE_WEATHER_ERROR: ["I don't know the weather this far ahead.",
                                      "There is not prediction data for your requested date yet."],
    ErrorCode.NOT_IMPLEMENTED_ERROR: ["This function is not implemented."],
    ErrorCode.LOCATION_ERROR: ["I can't find the location."],
    ErrorCode.PAST_WEATHER_ERROR: ["I don't know the weather of the past.",
                                    "I am a forecasting service not a historian."],
    ErrorCode.NO_WEATHER_FOR_DAY_ERROR: ["There seems to be no weather for today."],
    ErrorCode.DATE_ERROR: ["Something is wrong with the date."],
    ErrorCode.API_TIMEOUT_ERROR: ["API Key was used to often, try again later."],
    ErrorCode.CONFIG_ERROR: ["There seems to be something wrong with the configuration file."],
    ErrorCode.TIME_ERROR: ["Something is wrong with the time."],
    ErrorCode.GENERAL_ERROR: ["Something went wrong."]
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


# used for detailed report of the day
fixed_times = {
    FixedTimes.MORNING: "Morning",
    FixedTimes.AFTERNOON: "Afternoon",
    FixedTimes.EVENING: "Evening"
}

# temperature report
temperature_answers = {
    "general_temperature_full": ["The temperature {when} {where}: "],
    TemperatureType.GENERAL: {
        "": ["The temperature {when} {where} is {temperature}."]
    },
    TemperatureType.COLD: {
        "true": ["Yes, it will be cold {where} {when}. The temperature will be {temperature}."],
        "false": ["No, {when} {where} will not be cold. The temperature will be {temperature}."]
    },
    TemperatureType.WARM: {
        "true": ["Yes, it will be warm {where} {when}. The temperature will be {temperature}."],
        "false": ["No, {when} {where} will not be warm. The temperature will be {temperature}."]
    }
}


def format_temperature_output(min_temperature, max_temperature):
    if min_temperature == max_temperature:
        return str(utils.normal_round(min_temperature)) + " degrees"  # Centigrade/Fahrenheit is handled through setting in config.ini
    else:
        return "between " + str(utils.normal_round(min_temperature)) + " and " + str(utils.normal_round(max_temperature)) + " degrees"


# condition report
condition_answers = {
    "general_weather_full": ["The weather {when} {where}: ", "Weather for {when} {where}: "],
    ConditionType.GENERAL: {
        "": ["The weather {when} {where}: {weather}."]
    },
    ConditionType.RAIN: {
        "true": ["{when} could be rainy {where}."],
        "false": ["It will not rain {when} {where}."]
    },
    ConditionType.SNOW: {
        "true": ["{when} {where} might have snow."],
        "false": ["There will be no snow {when} {where}."]
    },
    ConditionType.THUNDERSTORM: {
        "true": ["{when} could have a thunderstorm {where}."],
        "false": ["I don't know about a thunderstorm {when} {where}."]
    },
    ConditionType.CLOUDS: {
        "true": ["{when} {where} could be cloudy."],
        "false": ["{when} {where} will not be cloudy."]
    },
    ConditionType.SUN: {
        "true": ["{when} {where} will be sunny."],
        "false": ["{when} {where} won't be sunny."]
    },
    ConditionType.STARS: {
        "true": ["You can see the stars {when} {where}."],
        "false": ["No stars {when} {where}."]
    },
    ConditionType.CLEAR: {
        "true": ["The sky will be clear {when} {where}."],
        "false": ["No clear skies {when} {where}."]
    },
    ConditionType.MIST: {
        "true": ["{when} {where} might be foggy."],
        "false": ["{when} {where} will have no fog."]
    },
    ConditionType.UNKNOWN: {
        "": ["I don't know what you want to know."]
    }
}

general_answers = {
    "affirmative": ["Yes"],
    "negative": ["No"],
    "alternate_weather": ["The weather will be: {weather}", "Instead it will be: {weather}", "Instead: {weather}", "Here the general weather: {weather}"]
}


def combine_conditions(condition_list):
    if isinstance(condition_list, list):
        if len(condition_list) == 0:
            return ""
        elif len(condition_list) == 1:
            return condition_list[0]
        else:
            combined = condition_list[0]
            for x in condition_list[1:-1]:
                combined += ", " + x
            combined += " and " + condition_list[-1]
            return combined


# items

items = WeatherItemList()
items.add_item("umbrella", "an", "", ["rain", "snow"])
items.add_item("raincoat", "a", "", ["rain", "wind"])
items.add_item("rain coat", "a", "", ["rain", "wind"])
items.add_item("rubber boots", "", "", ["rain"])
items.add_item("pair of rubber boots", "a", "", ["rain"])
items.add_item("sandals", "", "", ["warm", "sun"])
items.add_item("sunglasses", "", "", ["sun"])
items.add_item("sunscreen", "", "", ["sun"])
items.add_item("boots", "", "", ["cold", "wind"])
items.add_item("scarf", "a", "", ["cold"])
items.add_item("gloves", "", "", ["cold"])
items.add_item("hat", "a", "", ["cold"])
items.add_item("wool hat", "a", "", ["cold"])
items.add_item("hoodie", "a", "", ["cold"])
items.add_item("sun hat", "a", "", ["sun"])
items.add_item("cap", "a", "", ["sun"])
items.add_item("parasol", "a", "", ["sun"])
items.add_item("boots", "", "", ["rain", "cold", "wind"])
items.add_item("pair of boots", "a", "", ["rain", "cold", "wind"])
items.add_item("sun screen", "", "", ["sun"])
items.add_item("pair of gloves", "a", "", ["cold"])
items.add_item("sneakers", "", "", ["cold", "wind"])
items.add_item("winter boots", "", "", ["cold", "snow"])
items.add_item("pair of winter boots", "a", "", ["cold", "snow"])
items.add_item("winter coat", "a", "", ["cold", "snow"])
items.add_item("sandals", "", "", ["warm", "sun"])
items.add_item("pair of sandals", "a", "", ["warm", "sun"])

rain_items = items.get_item_names_for_condition("rain")
warm_items = items.get_item_names_for_condition("warm")
cold_items = items.get_item_names_for_condition("cold")
sun_items = items.get_item_names_for_condition("sun")

item_answers = {
    "rain": ["It could be rainy {when} {where}. Taking {item} might be a good idea.",
             "Yes, taking {item} {when} {where} makes sense."],
    "no_rain": ["There should be no rain {when} {where}. {item} is probably not necessary.",
                "No, you will most likely not need {item}. No rain is expected {when} {where}."],
    "warm_and_sunny": [
        "It will be warm {when} {where} and the sun might come out during the day. {item} might be a good idea."],
    "not_warm_and_sunny": [
        "It will not exactly be warm {when} {where} but it might still be sunny. {item} could still be useful."],
    "not_sunny": ["It will not be sunny {when} {where}. {item} might not be necessary.",
                  "There is not going to be a lot of sunshine {when} {where}. Therefore, you might not need {item}."],
    "nighttime": ["It is dark {when} {where} so you won't need {item}."],
    "warm": ["It will be warm {when} {where}. {item} might be a good idea."],
    "not_warm": ["It will not be warm {when} {where}, so {item} might not help."],
    "cold": ["It will be cold {when} {where}. {item} might be a good idea."],
    "not_cold": ["It will not be cold {when} {where}, so {item} might not help."],
    "unknown_item": ["I have no idea what {item} is, I am sorry."]
}


def format_item_for_output(item_name):
    if items.is_in_list(item_name):
        return items.get_item(item_name).format_for_output()
    else:
        return item_name
