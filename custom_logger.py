import logging
import datetime
import sys

import pytz


def custom_logger(path):
    logging_format = '%(asctime)s - %(levelname)-5s - %(name)s.%(funcName)s[%(lineno)d]: %(message)s'
    date_format = "%Y-%m-%d %H:%M:%S"
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(path, encoding='utf-8')
    file_handler.terminator = '\n'
    file_handler.setFormatter(logging.Formatter(logging_format, date_format))
    logging.Formatter.converter = custom_time
    logger.addHandler(file_handler)
    sys.excepthook = exception_to_log
    return logger


def exception_to_log(error_type, error_value, error_traceback):
    if issubclass(error_type, KeyboardInterrupt):
        sys.__excepthook__(error_type, error_value, error_traceback)
        return
    logging.exception("Uncaught exception: ", exc_info=(error_type, error_value, error_traceback))


def custom_time(*args):
    converted = datetime.datetime.now(pytz.timezone('Europe/Berlin'))
    return converted.timetuple()
