"""
Answer Rhasspy GetForecast intents received via mqtt in a hermes like fashion
"""

import paho.mqtt.client as mqtt
import datetime
import json
import logging
import os
import sys
import pytz
import rhasspy_weather.weather as weather
from custom_logger import custom_logger

logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), '/tmp/rhasspy_weather_mqtt.log')
root_logger = custom_logger(logfile)
log = logging.getLogger(__name__)

def speech(text):
    global o
    o["speech"] = {"text": text}

def prepare_dict(hermes_dict):
    """
    Prepare a rhasspy type like dict from a hermes intent dict
    """
    intent = hermes_dict["intent"]["intentName"]
    out_dict = {}
    out_dict.update({"slots": {s["slotName"]:s["rawValue"] for s in hermes_dict["slots"]}})
    out_dict["intent"] = {"name": intent}
    return out_dict


def on_connect(client, userdata, flags,rc):
    print("Connected with result code "+str(rc))
    client.subscribe("hermes/intent/#")

def on_message(client, userdata, msg):
    # adapt topic if neccessary
    if msg.topic.startswith('hermes/intent'):
        m_decode=str(msg.payload.decode().replace('\'','"'))
        o = json.loads(m_decode)
        o = prepare_dict(o)
        intent = o['intent']['name']
        if intent == "GetTime":
            now = datetime.datetime.now(pytz.timezone('Europe/Berlin'))
            speech("Es ist %s Uhr %d." % (now.hour, now.minute))
            print(json.dumps(o))
        elif intent.startswith("GetWeatherForecast"):
            log.info("Detected Weather Intent")
            try:
                forecast = weather.get_weather_forecast(o, config_path="../rhasspy_weather_config.ini")
                print(json.dumps(o))
            except Exception as e:
                log.error(f'Error handling intent {o}:{e}')
        else:
            log.info("No intent found.")
            print(json.dumps(o))


client = mqtt.Client()
# Insert mqtt credentials here
client.username_pw_set(username="",password="")
client.on_connect = on_connect
client.on_message = on_message

# Insert mqtt brokerer details here
client.connect("127.0.0.1", 1883, 60)

client.loop_forever()
