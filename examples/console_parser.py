# thanks to ulno who wrote the console parser for rhasspy_weather (https://github.com/ulno/cli_weather) that I used as an example

import argparse
import json
import logging
import os
import sys

from custom_logger import custom_logger
from rhasspy_weather.weather import get_weather_forecast


logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'console_output.log')
root_logger = custom_logger(logfile)
log = logging.getLogger(__name__)


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--day', help='Forecast day (sunday, monday, ...) or "day month".')  # when_day
    parser.add_argument('-t', '--time', help='Forecast time')  # when_time
    parser.add_argument('-l', '--location', help='Forecast location')  # location
    parser.add_argument('-i', '--item', help='Is a specific item (like umbrella) needed/recommended.')  # item
    parser.add_argument('-c', '--condition', help='Is a specific condition active at given time.')  # condition
    parser.add_argument('-e', '--temperature', help='Temperature forecast.')  # temperature
    parser.add_argument('-f', '--configfile', help="Path to the config file")
    parser.add_argument('-j', '--json', help="Receive json in rhasspy intent event format as one parameter string or via stdin when this is set to a dash (-) and forward that to rhasspy_weather component.")

    args = parser.parse_args()
    config_path = None
    if args.configfile is not None:
        config_path = args.configfile
    weather_input = args
    if args.json is not None:
        if args.json == "-":
            # read and parse json from stdin and send it to rhasspy_weather
            weather_input = json.load(sys.stdin)
        else:
            weather_input = json.loads(args.json, ensure_ascii=False)

    get_weather_forecast(weather_input, config_path=config_path)


if __name__ == '__main__':
    parse()
