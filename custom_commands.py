#!/usr/bin/python3

import datetime
import json
import logging
import os
import sys
import pytz
import rhasspy_weather.weather as weather
from custom_logger import custom_logger

logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output.log')
root_logger = custom_logger(logfile)
log = logging.getLogger(__name__)

debug_mode = False

if "-d" in sys.argv:
    debug_mode = True


def speech(text):
    global o
    o["speech"] = {"text": text}


# get json from stdin and load into python dict
if debug_mode:
    o = json.loads(
        '{ "entities": [], "intent": {"confidence": 1, "name": "GetWeatherForecast"}, "raw_text": "wie wird das wetter", "raw_tokens": ["wie", "wird", "das", "wetter"], "recognize_seconds": 0.08515081899531651, "slots": {}, "speech_confidence": 1, "text": "wie wird das wetter", "tokens": ["wie", "wird", "das", "wetter"], "wakeword_id": null}')
else:
    o = json.loads(sys.stdin.read())

intent = o["intent"]["name"]

log.info("\n\nCustom Script Started")

if intent == "GetTime":
    now = datetime.datetime.now(pytz.timezone('Europe/Berlin'))
    speech("Es ist %s Uhr %d." % (now.hour, now.minute))
    print(json.dumps(o))
elif intent.startswith("GetWeatherForecast"):
    log.info("Detected Weather Intent")
    forecast = weather.get_weather_forecast(o)
else:
    log.info("No intent found.")
    print(json.dumps(o))
