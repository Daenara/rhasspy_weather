import logging
import math

log = logging.getLogger(__name__)


def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)


def format_string(input_string):
    input_string = input_string.replace("..", ".")
    input_string = input_string.replace(" .", ".")
    input_string = input_string.replace("   ", " ")
    input_string = input_string.replace("  ", " ")
    input_string = input_string.replace(" :", ":")
    input_string = input_string[0].capitalize() + input_string[1:]
    return input_string