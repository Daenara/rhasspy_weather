import datetime
from rhasspy_weather.data_types.status import StatusCode

# used in parsers
weekday_names = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
month_names = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
named_days = {"heute":0, "morgen":1, "übermorgen":2}
named_times = {
    "Morgen": (datetime.time(6, 0), datetime.time(10, 0)),
    "Vormittag": (datetime.time(10, 0), datetime.time(12, 0)), 
    "Mittag": (datetime.time(12, 0), datetime.time(14, 0)), 
    "Nachmittag": (datetime.time(15, 0), datetime.time(18, 0)), 
    "Abend": (datetime.time(18, 0), datetime.time(22, 0)), 
    "Nacht": (datetime.time(22, 0), datetime.time(7, 0))
}
named_times_synonyms = {
    "früh": "Morgen"
}

# used in status.py to output status messages
status_response = {
    StatusCode.NORMAL: ["Sieht alles normal aus."],
    StatusCode.NO_NETWORK_ERROR: ["Es ist leider kein Internet verfügbar.", 
                                  "Ich bin nicht mit dem Internet verbunden.", 
                                  "Es ist kein Internet vorhanden."],
    StatusCode.API_ERROR: ["Das Wetter konnte nicht abgerufen werden. Vermutlich ist der API-Schlüssel ungültig.", 
                           "Fehler beim Abrufen. Der API-Schlüssel ist ungültig."],
    StatusCode.FUTURE_WEATHER_ERROR: ["So weit in die Zukunft kenne ich das Wetter nicht.",
                                      "Ich kann nicht soweit in die Zukunft sehen.",
                                      "Das Wetter für diesen Tag wurde noch nicht beschlossen.",
                                      "Dieses Datum liegt zu weit in der Zukunft."],
    StatusCode.NOT_IMPLEMENTED_ERROR: ["Diese Funktion wird noch nicht unterstützt.", 
                                      "Ich weiß nicht wie ich diese Anfrage verarbeiten soll."],
    StatusCode.LOCATION_ERROR: ["Ich kann die angegebene Stadt nich finden. Vielleicht habe ich sie nicht richtig verstanden"],
    StatusCode.PAST_WEATHER_ERROR : ["Ich kann dir das Wetter aus der Vergangenheit leider nicht sagen."],
    StatusCode.NO_WEATHER_FOR_DAY_ERROR: ["Es ist so kurz vor Mitternacht, dass ich das Wetter für heute nicht abrufen kann."],
    StatusCode.DATE_ERROR: ["Irgendwas stimmt mit dem Datum nicht."],
    StatusCode.API_TIMEOUT_ERROR: ["Mit diesem API-Schlüssel wurden zu viele Anfragen gesenden. Versuche es später erneut."],
    StatusCode.CONFIG_ERROR: ["Es gab ein Problem beim Laden der Konfigurationsdatei."],
    StatusCode.TIME_ERROR: ["Irgendwas stimmt mit der angegebenen Zeit nicht."],
    StatusCode.GENERAL_ERROR: ["Es ist ein Fehler aufgetreten.", "Hier ist ein Fehler aufgetreten."]
}

# used in report.py

# condition report

condition_answers = {
    "general_weather": ["Das Wetter {when} {where}: {weather}.", 
               "{when} {where} ist das Wetter: {weather}.", 
               "Wetter {when} {where}: {weather}."],
    "rain_true": ["Ja, {when} wird es {where} regnen.",
                 "Ja, {when} gibt es {where} Regen.",
                 "Ja, es regnet {when} {where}.",
                 "Ja, {when} regnet es {where}."],
    "rain_false": ["Nein, es regnet {when} {where} nicht. Das Wetter ist: {weather}.",
                  "Nein, {when} regnet es {where} nicht. Stattdessen ist das Wetter: {weather}.",
                  "Nein, {when} gibt es keinen Regen {where}. Das Wetter ist: {weather}."],
    "snow_true": ["Ja, {when} wird es {where} schneien.",
                 "Ja, {when} gibt es {where} Schnee.",
                 "Ja, es schneit {when} {where}.",
                 "Ja, {when} schneit es {where}."],
    "snow_false": ["Nein, es schneit {when} {where} nicht. Das Wetter ist: {weather}.",
                  "Nein, {when} schneit es {where} nicht. Stattdessen ist das Wetter: {weather}.",
                  "Nein, {when} gibt es keinen Schnee {where}. Das Wetter ist: {weather}."],
    "thunderstorm_true": ["Ja, {when} gibt es {where} Gewitter."],
    "thunderstorm_false": ["Nein, {when} {where} gewittert es nicht. Das Wetter ist: {weather}."],
    "clouds_true": ["Ja, {when} kann es {where} bewölkt sein."],
    "clouds_false": ["Nein, {when} {where} ist es nicht bewölkt. Das Wetter ist: {weather}."],
    "sun_true": ["Ja, {when} {where} scheint die Sonne."],
    "sun_false": ["Nein, {when} {where} scheint keine Sonne. Das Wetter ist: {weather}."],
    "mist_true": ["Ja, {when} {where} ist es neblig."],
    "mist_false": ["Nein, {when} {where} ist es nicht neblig. Das Wetter ist: {weather}."]
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
            combined += " und " + conditions[-1]
            return combined

# items
rain_items = ["Regenmantel", "Schirm", "Gummistiefel", "Halbschuhe", "Kaputze", "Hut", "Regenschirm"]
warm_items = ["Sonnenbrille", "Sonnencreme", "Sonnenschirm", "Kappe", "Sonnenhut", "Sandalen"]
cold_items = ["Winterstiefel", "Mantel", "Schal", "Handschuhe", "Mütze"]

item_answers = {
    "rain": ["Es könnte {when} {where} regnen, {item} keine schlechte Idee.", "Es könnte {when} {where} Regen geben. {item} keine schlechte Idee."],
    "no_rain": ["Es ist {when} {where} kein Regen gemeldet. {item} also vermutlich unnötig."],
    "warm_and_sunny": ["Es ist {when} warm {where} und tagsüber kommt die Sonne raus. {item} daher eine gute Idee."],
    "not_warm_and_sunny": ["Es ist {when} {where} nicht sonderlich warm aber trotzdem sonnig. {item} vielleicht trotzdem nützlich."],
    "not_sunny": ["Es ist {when} {where} nicht unbedingt sonnig. {item} vermutlich eher überflüssig."],
    "cold": ["Es ist {when} kalt {where}. {item} daher eine gute Idee."],
    "not_cold": ["Es ist {when} {where} nicht sonderlich kalt. {item} daher eher unnötig."],
    "unknown_item": ["Ich bin mir nicht sicher, was ein {item} ist, tut mir leid."]
}

def format_item_for_output(item):
    if item in ["Regenmantel", "Schirm", "Hut", "Sonnenhut", "Mantel", "Schal", "Sonnenschirm", "Regenschirm"]:
        return "ein " + item + " ist"
    elif item in ["Kaputze", "Kappe", "Mütze", "Sonnenbrille"]:
        return "eine " + item + " ist"
    elif item in ["Gummistiefel", "Halbschuhe", "Sandalen", "Handschuhe", "Winterstiefel"]:
        return item + " sind"
    elif item in ["Sonnencreme"]:
        return item + " ist"
    else: 
        return item