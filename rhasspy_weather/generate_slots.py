#!/usr/bin/python3
import datetime
import logging
import os
import sys

import pytz

from rhasspy_weather.data_types.config import get_config

logging_format = '%(asctime)s - %(levelname)-5s - %(name)s.%(funcName)s[%(lineno)d]: %(message)s'
logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), 'output.log'), format=logging_format,
                    datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)


def custom_time(*args):
    converted = datetime.datetime.now(pytz.timezone('Europe/Berlin'))
    return converted.timetuple()


logging.Formatter.converter = custom_time

config = get_config()
slots = {
    "conditions": "list(config.locale.condition_types.keys()) + list(config.locale.condition_synonyms.keys())",
    "items": "list(config.locale.items.get_all_item_names())",
    "named_days": "list(config.locale.named_days.keys()) + list(config.locale.named_days_synonyms.keys())",
    "named_times": "list(config.locale.named_times.keys()) + list(config.locale.named_times_synonyms.keys())",
    "temperatures": "list(config.locale.temperature_types.keys()) + list(config.locale.temperature_synonyms.keys())"
}

if __name__ == "__main__":
    executable = False
    if "-x" in sys.argv:
        executable = True

    for key in slots.keys():
        f = open(os.path.join("slot_programs", key), mode="w", encoding="utf-8")
        if executable:
            f = open(os.path.join("slot_programs", key), mode="w", encoding="utf-8")
            out = "#!/usr/bin/python3\n"
            out += "from rhasspy_weather.data_types.config import get_config\n"
            out += "config = get_config()\n"
            out += "output_list = " + slots[key] + "\n\n"
            out += "for output in output_list:\n"
            out += "\tprint(output)"
            f.write(out)
        else:
            f = open(os.path.join("slots", key), mode="w", encoding="utf-8")
            for s in eval(slots[key]):
                f.write(s + "\n")
        f.close()
