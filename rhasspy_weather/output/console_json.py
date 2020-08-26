import json
import logging

log = logging.getLogger(__name__)


def output_response(output):
    log.debug("Selected output: console_json")
    print(json.dumps(json.loads(output)))


def parse_config(config_parser):
    pass
