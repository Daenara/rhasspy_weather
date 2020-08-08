import json
import logging

log = logging.getLogger(__name__)


def output_response(output):
    log.debug("output_console")
    print(json.dumps(json.loads(output)))
