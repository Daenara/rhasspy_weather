import random

from rhasspy_weather.data_types.condition import ConditionType
from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.error import WeatherError, ErrorCode
import rhasspy_weather.data_types.item_list as item_list
from rhasspy_weather.data_types.report import WeatherReport
from rhasspy_weather.data_types.request import Grain, ForecastType
from rhasspy_weather.data_types.temperature import TemperatureType
from rhasspy_weather.data_types.weather_type import WeatherType


def generate_report(request, weather):
    config = get_config()
    timezone = config.timezone
    locale = config.locale

    items = item_list.items.get_items_for_weather(ConditionType.RAIN)

    if not (request.grain == Grain.DAY or request.grain == Grain.HOUR):
        raise WeatherError(ErrorCode.NOT_IMPLEMENTED_ERROR)

    if config.detail and request.forecast_type is not ForecastType.ITEM:
        pass
    else:
        report = WeatherReport(request, weather)
        report.report()

    return report


def output_date_and_time(request, locale):
    if request.date_specified != "":
        date = request.date_specified
    else:
        date = locale.format_output_date(request)
    if request.time_specified != "":
        time = request.time_specified
    else:
        if request.grain == Grain.HOUR:
            time = locale.format_output_time(request)
        else:
            time = ""

    if request.grain == Grain.HOUR:
        return date + " " + time
    return date


def output_location(request, locale):
    return locale.format_output_location(request.location.name) if request.location_specified else ""
