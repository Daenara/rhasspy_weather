import datetime

from rhasspy_weather.data_types.item import NounType
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
    ErrorCode.MQTT_CONNECTION_ERROR: ["I can't contact the mqtt broker."],
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
    TemperatureType.GENERAL: ["The temperature {when} {where} is {temperature}."],
    TemperatureType.COLD: {
        "true": ["Yes, it will be cold {where} {when}."],
        "false": ["No, {when} {where} will not be cold.."]
    },
    TemperatureType.WARM: {
        "true": ["Yes, it will be warm {where} {when}."],
        "false": ["No, {when} {where} will not be warm."]
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
    ConditionType.GENERAL: ["The weather {when} {where}: {weather}."],
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
        "false": ["{when} {where} won't be sunny."],
        "night": ["It is dark {when} {where}, the sun can't shine."]
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
    ConditionType.UNKNOWN: ["I don't know what you want to know."]
}

general_answers = {
    "affirmative": ["Yes"],
    "negative": ["No"],
    "item_needed": ["{article} {noun} sounds useful", "{article} {noun} could help", "{article} {noun} {verb} a good idea"],
    "item_not_needed": ["{article} {noun} {verb} {when} {where} useless"],
    "weather": ["The weather will be: {weather}", "The Weather: {weather}"]
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
grammar = {
    NounType.SINGULAR: "is",
    NounType.PLURAL: "are"
}

items = WeatherItemList()
items.add_item("umbrella", NounType.SINGULAR, article="an", weather_list=[ConditionType.RAIN, ConditionType.SNOW])
items.add_item("raincoat", NounType.SINGULAR, article="a", weather_list=[ConditionType.RAIN, ConditionType.WIND])
items.add_item("rain coat", NounType.SINGULAR, article="a", weather_list=[ConditionType.RAIN, ConditionType.WIND])
items.add_item("rubber boots", NounType.PLURAL, weather_list=[ConditionType.RAIN])
items.add_item("pair of rubber boots", NounType.SINGULAR, article="a", weather_list=[ConditionType.RAIN])
items.add_item("sandals", NounType.PLURAL, weather_list=[TemperatureType.WARM, ConditionType.SUN])
items.add_item("sunglasses", NounType.PLURAL, weather_list=[ConditionType.SUN])
items.add_item("sunscreen", NounType.SINGULAR, weather_list=[ConditionType.SUN])
items.add_item("boots", NounType.PLURAL, weather_list=[TemperatureType.COLD, ConditionType.WIND])
items.add_item("scarf", NounType.SINGULAR, article="a", weather_list=[TemperatureType.COLD])
items.add_item("gloves", NounType.PLURAL, weather_list=[TemperatureType.COLD])
items.add_item("hat", NounType.SINGULAR, article="a", weather_list=[TemperatureType.COLD])
items.add_item("wool hat", NounType.SINGULAR, article="a", weather_list=[TemperatureType.COLD])
items.add_item("hoodie", NounType.SINGULAR, article="a", weather_list=[TemperatureType.COLD])
items.add_item("sun hat", NounType.SINGULAR, article="a", weather_list=[ConditionType.SUN])
items.add_item("cap", NounType.SINGULAR, article="a", weather_list=[ConditionType.SUN])
items.add_item("parasol", NounType.SINGULAR, article="a", weather_list=[ConditionType.SUN])
items.add_item("boots", NounType.PLURAL, weather_list=[ConditionType.RAIN, TemperatureType.COLD, ConditionType.WIND])
items.add_item("pair of boots", NounType.SINGULAR, article="a", weather_list=[ConditionType.RAIN, TemperatureType.COLD, ConditionType.WIND])
items.add_item("sun screen", NounType.SINGULAR, weather_list=[ConditionType.SUN])
items.add_item("pair of gloves", NounType.SINGULAR, article="a", weather_list=[TemperatureType.COLD])
items.add_item("sneakers", NounType.PLURAL, weather_list=[TemperatureType.COLD, ConditionType.WIND])
items.add_item("winter boots", NounType.PLURAL, weather_list=[TemperatureType.COLD, ConditionType.SNOW])
items.add_item("pair of winter boots", NounType.SINGULAR, article="a", weather_list=[TemperatureType.COLD, ConditionType.SNOW])
items.add_item("winter coat", NounType.SINGULAR, article="a", weather_list=[TemperatureType.COLD, ConditionType.SNOW])
items.add_item("sandals", NounType.PLURAL, weather_list=[TemperatureType.WARM, ConditionType.SUN])
items.add_item("pair of sandals", NounType.SINGULAR, article="a", weather_list=[TemperatureType.WARM, ConditionType.SUN])

