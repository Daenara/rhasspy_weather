from enum import Enum
import random

import inspect
import logging

log = logging.getLogger(__name__)

class StatusCode(Enum):
    NORMAL = 0
    NO_NETWORK_ERROR = 1
    API_ERROR = 2
    FUTURE_WEATHER_ERROR = 3
    NOT_IMPLEMENTED_ERROR = 4
    LOCATION_ERROR = 5
    PAST_WEATHER_ERROR = 6
    NO_WEATHER_FOR_DAY_ERROR = 7
    DATE_ERROR = 8
    API_TIMEOUT_ERROR = 9
    CONFIG_ERROR = 10
    TIME_ERROR = 11
    GENERAL_ERROR = -1

class Status:
    def __init__(self, status_code=StatusCode.NORMAL):
        self.status_code = status_code

    @property
    def status_code(self):
        return self.__status_code  
    @status_code.setter
    def status_code(self, val):
        self.__status_code = val
        
    @property
    def is_error(self):
        if self.status_code == StatusCode.NORMAL:
            return False
        return True

    def set_status(self, val):
        self.status_code = val
        self.status_response()

    def status_response(self):
        if self.status_code == StatusCode.NORMAL:
            response = "Sieht alles normal aus."
        if self.status_code == StatusCode.NO_NETWORK_ERROR:
            response = random.choice(["Es ist leider kein Internet verfügbar.",
                                      "Ich bin nicht mit dem Internet verbunden.",
                                      "Es ist kein Internet vorhanden."])
        elif self.status_code == StatusCode.API_ERROR:
            response = random.choice(["Das Wetter konnte nicht abgerufen werden. "+\
                                        "Vermutlich ist der API-Schlüssel ungültig.",
                                      "Fehler beim Abrufen. Der API-Schlüssel ist ungültig."])
        elif self.status_code == StatusCode.FUTURE_WEATHER_ERROR:
            response = random.choice(["So weit in die Zukunft kenne ich das Wetter nicht.",
                                      "Ich kann nicht soweit in die Zukunft sehen.",
                                      "Das Wetter für diesen Tag wurde noch nicht beschlossen.",
                                      "Dieses Datum liegt zu weit in der Zukunft."])
        elif self.status_code == StatusCode.NOT_IMPLEMENTED_ERROR:
            response = random.choice(["Diese Funktion wird noch nicht unterstützt.", 
                                      "Ich weiß nicht wie ich diese Anfrage verarbeiten soll."])
        elif self.status_code == StatusCode.LOCATION_ERROR:
            response = "Ich kann die angegebene Stadt nich finden. Vielleicht habe ich sie nicht richtig verstanden"
        elif self.status_code == StatusCode.PAST_WEATHER_ERROR:
            response = "Ich kann dir das Wetter aus der Vergangenheit leider nicht sagen."
        elif self.status_code == StatusCode.NO_WEATHER_FOR_DAY_ERROR:
            response = "Es ist so kurz vor Mitternacht, dass ich das Wetter für heute nicht abrufen kann."
        elif self.status_code == StatusCode.DATE_ERROR:
            response = "Irgendwas stimmt mit dem Datum nicht."
        elif self.status_code == StatusCode.API_TIMEOUT_ERROR:
            response = "Mit diesem API-Schlüssel wurden zu viele Anfragen gesenden. Versuche es später erneut."
        else:
            response = random.choice(["Es ist ein Fehler aufgetreten.", "Hier ist ein Fehler aufgetreten."])
        if self.is_error: 
            log.error("Status: {0} - {1}".format(StatusCode(self.status_code), response))
        else:
            log.info("Status: {0} - {1}".format(StatusCode(self.status_code), response))
        return response