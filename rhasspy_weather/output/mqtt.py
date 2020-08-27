import logging

import paho.mqtt.client as mqtt

from rhasspy_weather.data_types.error import WeatherError, ErrorCode, ConfigError

log = logging.getLogger(__name__)

mqtt_address = None
mqtt_port = 1883
mqtt_user = None
mqtt_password = None
mqtt_topic = "rhasspy_weather/response"


def output_response(output):
    log.debug("Selected output: mqtt_json")
    try:
        client = mqtt.Client()
        client.username_pw_set(mqtt_user, mqtt_password)
        client.connect(mqtt_address, mqtt_port, 60)
        client.publish(mqtt_topic, output)
    except ConnectionRefusedError as e:
        raise WeatherError(ErrorCode.MQTT_CONNECTION_ERROR, e.strerror)


def parse_config(config_parser):
    global mqtt_address, mqtt_port, mqtt_topic, mqtt_user, mqtt_password
    section = config_parser["mqtt"]

    if section is None:
        log.error(
            f"Output is set to {section} but that section is missing in the config. Please refer to 'config.default' for an example config.")

    mqtt_address = section.get("address")
    if mqtt_address is None or mqtt_address is "":
        raise ConfigError("MQTT Error", "No mqtt address set. This is required for rhasspy weather to work.", ErrorCode.CONFIG_ERROR)

    port = section.get("port")
    if port.isnumeric():
        mqtt_port = port

    topic = section.get("topic")
    if topic is not "":
        mqtt_topic = topic

    user = section.get("user")
    password = section.get("password")

    if user is not None and user is not "" and password is not None and password is not "":
        mqtt_user = user
        mqtt_password = password
