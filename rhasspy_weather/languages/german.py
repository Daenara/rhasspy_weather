import datetime

from rhasspy_weather.utils import utils, dt_utils
from rhasspy_weather.data_types.condition import ConditionType
from rhasspy_weather.data_types.item_list import WeatherItemList
from rhasspy_weather.data_types.error import ErrorCode

# general stuff
from rhasspy_weather.data_types.fixed_times import FixedTimes
from rhasspy_weather.data_types.temperature import TemperatureType

language_code = "de"

# used in parsers
weekday_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
month_names = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
               "November", "Dezember"]
named_days = {"heute": 0, "morgen": 1, "übermorgen": 2, "weihnachten": dt_utils.get_date_with_year(24, 12)}
named_days_synonyms = {"heilig abend": "weihnachten"}
named_times = {
    "Morgen": (datetime.time(6, 0), datetime.time(10, 0)),
    "Vormittag": (datetime.time(10, 0), datetime.time(12, 0)),
    "Mittag": (datetime.time(12, 0), datetime.time(14, 0)),
    "Nachmittag": (datetime.time(14, 0), datetime.time(18, 0)),
    "Abend": (datetime.time(18, 0), datetime.time(22, 0)),
    "Nacht": (datetime.time(22, 0), datetime.time(6, 0))
}
named_times_synonyms = {
    "früh": "Morgen"
}
condition_types = {
    "regen": ConditionType.RAIN,
    "schnee": ConditionType.SNOW,
    "nebel": ConditionType.MIST,
    "wolken": ConditionType.CLOUDS,
    "gewitter": ConditionType.THUNDERSTORM,
    "sonne": ConditionType.SUN,
    "sterne": ConditionType.STARS,
    "klar": ConditionType.CLEAR,
    "wind": ConditionType.WIND
}
condition_synonyms = {
    "regnet": "regen",
    "schneit": "schnee",
    "nebelt": "nebel",
    "wolkig": "wolken",
    "bewölkt": "wolken",
    "gewittert": "gewitter",
    "sonnig": "sonne",
    "windig": "wind",
    "windet": "wind",
    "nieselt": "regen",
    "niesel": "regen",
    "schüttet": "regen",
    "schneien": "schnee",
    "regnen": "regen",
    "gewittern": "gewitter",
    "donnern": "gewitter",
    "donnert": "gewitter",
    "blitzt": "gewitter",
    "blitzen": "gewitter",
    "donner": "gewitter",
    "blitze": "gewitter",
    "klarer himmel": "klar"
}
temperature_types = {
    "warm": TemperatureType.WARM,
    "kalt": TemperatureType.COLD
}
temperature_synonyms = {
    "heiß": "warm"
}


def format_userdefined_date(date):
    return "am " + date


def format_userdefined_time(hour, minutes=-1):
    if minutes == -1:
        return "um " + str(hour) + " Uhr"
    return "um " + str(hour) + " Uhr " + str(minutes)


# weather conditions

conditions = {
    ConditionType.WIND: {0: "Windstille", 1: "Windstille", 2: "leichte Briese", 3: "schwacher Wind", 4: "mäßiger Wind",
                         5: "frischer Wind", 6: "starker Wind", 7: "starker Wind", 8: "Sturm",
                         9: "Sturm", 10: "schwerer Sturm", 11: "orkanartiger Sturm", 12: "Orkan"},
    ConditionType.CLOUDS: {0: "Klarer Himmel", 1: "Ein paar Wolken", 2: "Leicht bewölkt", 3: "Bewölkt",
                           4: "Stark bewölkt"},
    ConditionType.RAIN: {0: "leichter Regen", 1: "mäßiger Regen", 2: "starker Regen", 3: "sehr starker Regen",
                         4: "extremer Regen"},
    ConditionType.SNOW: {0: "leichter Schneefall", 1: "Schneefall", 2: "starker Schneefall"},
    ConditionType.THUNDERSTORM: {0: "leichtes Gewitter", 1: "Gewitter", 2: "starkes Gewitter"}}

# used in error.py to output status messages
status_response = {
    ErrorCode.NO_NETWORK_ERROR: ["Es ist leider kein Internet verfügbar.",
                                  "Ich bin nicht mit dem Internet verbunden.",
                                  "Es ist kein Internet vorhanden."],
    ErrorCode.API_ERROR: ["Das Wetter konnte nicht abgerufen werden. Vermutlich ist der API-Schlüssel ungültig.",
                           "Fehler beim Abrufen. Der API-Schlüssel ist ungültig."],
    ErrorCode.FUTURE_WEATHER_ERROR: ["So weit in die Zukunft kenne ich das Wetter nicht.",
                                      "Ich kann nicht soweit in die Zukunft sehen.",
                                      "Das Wetter für diesen Tag wurde noch nicht beschlossen.",
                                      "Dieses Datum liegt zu weit in der Zukunft."],
    ErrorCode.NOT_IMPLEMENTED_ERROR: ["Diese Funktion wird noch nicht unterstützt.",
                                       "Ich weiß nicht wie ich diese Anfrage verarbeiten soll."],
    ErrorCode.LOCATION_ERROR: [
        "Ich kann die angegebene Stadt nich finden. Vielleicht habe ich sie nicht richtig verstanden"],
    ErrorCode.PAST_WEATHER_ERROR: ["Ich kann dir das Wetter aus der Vergangenheit leider nicht sagen."],
    ErrorCode.NO_WEATHER_FOR_DAY_ERROR: [
        "Es ist so kurz vor Mitternacht, dass ich das Wetter für heute nicht abrufen kann."],
    ErrorCode.DATE_ERROR: ["Irgendwas stimmt mit dem Datum nicht."],
    ErrorCode.API_TIMEOUT_ERROR: [
        "Mit diesem API-Schlüssel wurden zu viele Anfragen gesenden. Versuche es später erneut."],
    ErrorCode.CONFIG_ERROR: ["Es gab ein Problem beim Laden der Konfigurationsdatei."],
    ErrorCode.TIME_ERROR: ["Irgendwas stimmt mit der angegebenen Zeit nicht."],
    ErrorCode.GENERAL_ERROR: ["Es ist ein Fehler aufgetreten.", "Hier ist ein Fehler aufgetreten."]
}


# used in report.py

def format_output_location(location):
    return "in {0}".format(location.capitalize())


def format_output_date(request):
    date = "am " + request.readable_date

    if request.time_difference == 0:
        date = "heute"
    elif request.time_difference == 1:
        date = "morgen"
    else:
        temp_day = datetime.datetime.today().weekday() + request.time_difference
        if temp_day < 7:
            date = "am " + request.weekday
        elif temp_day < 14:
            date = "nächste Woche " + request.weekday
    return date


def format_output_time(request):
    return "um " + request.readable_start_time + " Uhr"


# used for detailed report of the day
fixed_times = {
    FixedTimes.MORNING: "Morgens",
    FixedTimes.AFTERNOON: "Mittags",
    FixedTimes.EVENING: "Abends"
}

# temperature report
temperature_answers = {
    "general_temperature_full": ["Die Temperaturen {when} {where}: ", "Temperaturen für {when} {where}: "],
    TemperatureType.GENERAL: {
        "": ["Die Temperatur {when} {where} ist {temperature}.",
             "Es hat {where} {temperature} {when}.",
             "Es hat {where} {when} {temperature}.",
             "Es hat {when} {temperature} {where}."]
    },
    TemperatureType.COLD: {
        "true": ["Ja, {when} {where} wird es kalt. Die Temperatur ist {temperature}."],
        "false": ["Nein, {when} {where} wird es nicht kalt. Die Temperatur ist {temperature}."]},
    TemperatureType.WARM: {
        "true": ["Ja, {when} {where} wird es warm. Die Temperatur ist {temperature}."],
        "false": ["Nein, {when} {where} wird es nicht warm. Die Temperatur ist {temperature}."]
    }
}


def format_temperature_output(min_temperature, max_temperature):
    if min_temperature == max_temperature:
        return str(utils.normal_round(min_temperature)) + " Grad"
    else:
        return "zwischen " + str(utils.normal_round(min_temperature)) + " und " + str(utils.normal_round(max_temperature)) + " Grad"


# condition report
condition_answers = {
    "general_weather_full": ["Der Wetterbericht {when} {where}: ",
                             "Wetterbericht für {when} {where}: ",
                             "Das Wetter {when} {where}: ",
                             "Das Wetter für {when} {where}: "],
    ConditionType.GENERAL: {
        "": ["Das Wetter {when} {where}: {weather}.",
             "{when} {where} ist das Wetter: {weather}.",
             "Wetter {when} {where}: {weather}."]
    },
    ConditionType.RAIN: {
        "true": ["{when} wird es {where} regnen.",
                 "{when} gibt es {where} Regen.",
                 "Es regnet {when} {where}.",
                 "{when} regnet es {where}."],
        "false": ["Es regnet {when} {where} nicht.",
                  "{when} regnet es {where} nicht.",
                  "{when} gibt es keinen Regen {where}."]
    },
    ConditionType.SNOW: {
        "true": ["{when} wird es {where} schneien.",
                 "{when} gibt es {where} Schnee.",
                 "Es schneit {when} {where}.",
                 "{when} schneit es {where}."],
        "false": ["Es schneit {when} {where} nicht.",
                  "{when} schneit es {where} nicht.",
                  "{when} gibt es keinen Schnee {where}."]
    },
    ConditionType.THUNDERSTORM: {
        "true": ["{when} gibt es {where} Gewitter."],
        "false": ["{when} {where} gewittert es nicht."]
    },
    ConditionType.CLOUDS: {
        "true": ["{when} kann es {where} bewölkt sein."],
        "false": ["{when} {where} ist es nicht bewölkt."]
    },
    ConditionType.SUN: {
        "true": ["{when} {where} scheint die Sonne."],
        "false": ["{when} {where} scheint keine Sonne."]
    },
    ConditionType.STARS: {
        "true": ["Man kann {when} {where} die Sterne sehen."],
        "false": ["Keine Sterne zu sehen {when} {where}."]
    },
    ConditionType.CLEAR: {
        "true": ["Der Himmel ist klar {when} {where}."],
        "false": ["Kein klarer Himmel {when} {where}."]
    },
    ConditionType.MIST: {
        "true": ["{when} {where} ist es neblig."],
        "false": ["{when} {where} ist es nicht neblig.."]
    },
    ConditionType.UNKNOWN: {
        "": ["Ich weiß nicht, was genau du wissen willst."]
    }
}

general_answers = {
    "affirmative": ["Ja"],
    "negative": ["Nein"],
    "alternate_weather": ["Das Wetter ist: {weather}", "Stattdessen ist das Wetter {weather}", "Stattdessen ist es {weather}", "Das Wetter: {weather}"]
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
            combined += " und " + condition_list[-1]
            return combined


# items
items = WeatherItemList()
items.add_item("Regenmantel", "ein", "ist", ["rain", "wind"])
items.add_item("Schirm", "ein", "ist", ["rain", "snow"])
items.add_item("Gummistiefel", "", "sind", ["rain"])
items.add_item("Halbschuhe", "", "sind", ["rain", "wind"])
items.add_item("Kaputze", "eine", "ist", ["rain"])
items.add_item("Hut", "ein", "ist", ["rain", "sun", "snow"])
items.add_item("Regenschirm", "ein", "ist", ["rain", "snow"])
items.add_item("T-Shirt", "ein", "ist", ["warm", "sun"])
items.add_item("Sandalen", "", "sind", ["warm", "sun"])
items.add_item("kurze Hosen", "", "sind", ["warm", "sun"])
items.add_item("leichte Kleidung", "", "ist", ["warm", "sun"])
items.add_item("Winterstiefel", "", "sind", ["cold", "snow"])
items.add_item("Mantel", "ein", "ist", ["cold", "rain", "snow", "wind"])
items.add_item("Schal", "ein", "ist", ["cold", "snow"])
items.add_item("Handschuhe", "", "sind", ["cold", "snow"])
items.add_item("Mütze", "eine", "ist", ["cold", "snow"])
items.add_item("dicke Kleidung", "", "ist", ["cold"])
items.add_item("Stiefel", "", "sind", ["rain", "cold", "snow", "wind"])
items.add_item("lange Hosen", "", "sind", ["wind", "cold", "snow"])
items.add_item("lange Unterhosen", "", "sind", ["cold", "snow"])
items.add_item("Fleece", "ein", "ist", ["cold", "wind"])
items.add_item("Sonnenhut", "ein", "ist", ["sun"])
items.add_item("Sonnenschirm", "ein", "ist", ["sun"])
items.add_item("Kappe", "eine", "ist", ["sun"])
items.add_item("Sonnenbrille", "eine", "ist", ["sun"])
items.add_item("Sonnencreme", "", "ist", ["sun"])
items.add_item("paar Gummistiefel", "ein", "ist", ["rain"])
items.add_item("paar lange Unterhosen", "ein", "ist", ["cold", "snow"])
items.add_item("paar Handschuhe", "ein", "ist", ["cold", "snow"])
items.add_item("paar Stiefel", "ein", "ist", ["rain", "cold", "snow", "wind"])
items.add_item("paar Sandalen", "ein", "ist", ["warm", "sun"])
items.add_item("paar Winterstiefel", "ein", "ist", ["cold", "snow"])
items.add_item("Winterjacke", "eine", "ist", ["cold", "snow"])

rain_items = items.get_item_names_for_condition("rain")
warm_items = items.get_item_names_for_condition("warm")
cold_items = items.get_item_names_for_condition("cold")
sun_items = items.get_item_names_for_condition("sun")

item_answers = {
    "rain": ["Es könnte {when} {where} regnen, {item} keine schlechte Idee.",
             "Es könnte {when} {where} Regen geben. {item} keine schlechte Idee."],
    "no_rain": ["Es ist {when} {where} kein Regen gemeldet. {item} also vermutlich unnötig."],
    "warm_and_sunny": ["Es ist {when} warm {where} und tagsüber kommt die Sonne raus. {item} daher eine gute Idee."],
    "not_warm_and_sunny": [
        "Es ist {when} {where} nicht sonderlich warm aber trotzdem sonnig. {item} vielleicht trotzdem nützlich."],
    "not_sunny": ["Es ist {when} {where} nicht unbedingt sonnig. {item} vermutlich eher überflüssig."],
    "nighttime": ["Es ist {when} {where} dunkel. Im Dunkeln ist {item} unnötig"],
    "warm": ["Es ist {when} warm {where}. {item} daher eine gute Idee."],
    "not_warm": ["Es ist {when} {where} nicht sonderlich warm. {item} vermutlich unnötig."],
    "cold": ["Es ist {when} kalt {where}. {item} daher eine gute Idee."],
    "not_cold": ["Es ist {when} {where} nicht sonderlich kalt. {item} daher eher unnötig."],
    "unknown_item": ["Ich bin mir nicht sicher, was ein {item} ist, tut mir leid."]
}


def format_item_for_output(item_name):
    if items.is_in_list(item_name):
        return items.get_item(item_name).format_for_output()
    else:
        return item_name