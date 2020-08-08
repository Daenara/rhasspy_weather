import json
import logging
from rhasspy_weather.data_types.config import get_config

import paho.mqtt.client as mqtt

log = logging.getLogger(__name__)


def output_response(output):
    log.debug("Selected output: mqtt_json")
    config = get_config()
    client = mqtt.Client()
    if not (config.mqtt_user == "" or config.mqtt_password == ""):
        client.username_pw_set(config.mqtt_user, config.mqtt_password)
    client.connect(config.mqtt_address, config.mqtt_port, 60)
    client.publish(config.mqtt_topic, json.dumps(json.loads(output)))
