import logging
from rhasspy_weather.data_types.config import get_config

log = logging.getLogger(__name__)

try:
    import paho.mqtt.client as mqtt
except ImportError:
    import subprocess
    import sys
    log.error("Requirement paho mqtt not installed, will be installed now")
    subprocess.run([sys.executable, "-m", "pip", "install", 'paho-mqtt'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
finally:
    import paho.mqtt.client as mqtt


def output_response(response, dummy):
    config = get_config()
    client = mqtt.Client()
    if not (config.mqtt_user == "" or config.mqtt_password == ""):
        client.username_pw_set(config.mqtt_user, config.mqtt_password)
    client.connect(config.mqtt_address, config.mqtt_port, 60)
    client.publish(config.mqtt_topic, response)
