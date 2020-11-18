import logging

log = logging.getLogger(__name__)


def output_response(output):
    log.debug("Selected output: return")
    return output


def parse_config(config):
    pass


def get_template():
    return "$weather_text"
