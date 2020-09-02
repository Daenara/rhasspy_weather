import random

from rhasspy_weather.data_types.condition import ConditionType
from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.error import WeatherError, ErrorCode
from rhasspy_weather.data_types.report import WeatherReport
from rhasspy_weather.data_types.request import Grain, ForecastType


def generate_report(request, forecast):
    config = get_config()
    timezone = config.timezone
    locale = config.locale

    if not (request.grain == Grain.DAY or request.grain == Grain.HOUR):
        raise WeatherError(ErrorCode.NOT_IMPLEMENTED_ERROR)

    report = WeatherReport(request, forecast)

    if request.forecast_type == ForecastType.TEMPERATURE:
        pass
    elif request.forecast_type == ForecastType.CONDITION:
        pass
    elif request.forecast_type == ForecastType.FULL:
        pass
    elif request.forecast_type == ForecastType.ITEM:
        if request.requested in locale.rain_items:
            if report.weather.is_weather_chance(ConditionType.RAIN):
                response_type = "rain"
            else:
                response_type = "no_rain"
        elif request.requested in locale.warm_items:
            if report.weather.max_temperature >= config.temperature_warm_from:
                response_type = "warm"
            else:
                response_type = "not_warm"
        elif request.requested in locale.sun_items:
            day_weather = forecast.weather_during_daytime(request)
            if day_weather is not None:
                if day_weather.is_weather_chance(ConditionType.CLEAR):
                    if report.weather.max_temperature >= config.temperature_warm_from:
                        response_type = "warm_and_sunny"
                    else:
                        response_type = "not_warm_and_sunny"
                else:
                    response_type = "not_sunny"
            else:
                response_type = "nighttime"
        elif request.requested in locale.cold_items:
            if report.weather.max_temperature < config.temperature_cold_to:
                response_type = "cold"
            else:
                response_type = "not_cold"
        else:
            response_type = "unknown_item"
        report.speech = random.choice(locale.item_answers[response_type]).format(when=output_date_and_time(request, locale),
                                                                               where=output_location(request, locale),
                                                                               item=locale.format_item_for_output(request.requested))

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
