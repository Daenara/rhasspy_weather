import logging
import requests

from rhasspy_weather.data_types.error import ConfigError

log = logging.getLogger(__name__)

rhasspy_url = None


def output_response(output):
    log.debug("Selected output: rhasspy_tts")
    if rhasspy_url is None:
        raise ConfigError("No URL found", "No rhasspy server url found.")
    headers = {"Content-Type": "text/plain"}
    url = rhasspy_url + "/api/text-to-speech?play=true"
    response = requests.post(url, data=output.encode(), headers=headers)


def parse_config(config):
    global rhasspy_url

    section = config.get_external_section("rhasspy")

    if section is not None:
        rhasspy_url = section.get("address")
        if rhasspy_url is None or rhasspy_url is "":
            raise ConfigError("RHASSPY_TTS ERROR", "No URL set for the rhasspy server.")


def get_template():
    return "$speech"
