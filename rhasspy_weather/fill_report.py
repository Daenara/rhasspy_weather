from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.error import WeatherError, ErrorCode
from rhasspy_weather.data_types.report import WeatherReport
from rhasspy_weather.data_types.request import Grain, ForecastType


def generate_report(request, weather):
    config = get_config()

    if not (request.grain == Grain.DAY or request.grain == Grain.HOUR):
        raise WeatherError(ErrorCode.NOT_IMPLEMENTED_ERROR)

    if config.detail and request.forecast_type is not ForecastType.ITEM:
        pass
    else:
        report = WeatherReport(request, weather)
        report.report()

    return report
