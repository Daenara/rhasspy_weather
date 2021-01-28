import datetime
import json

import pytest
from rhasspy_weather import weather
import tests.data.parser_data as intent
from rhasspy_weather.data_types.request import WeatherRequest
from rhasspy_weather.data_types.request import ForecastType, Grain, DateType
from rhasspy_weather.data_types.error import WeatherError, ErrorCode
#from tests.conftest import mock_config_detail_true, mock_config_detail_false, mock_request_401, mock_request_404, \
#    mock_request_200, request_full_weather_day, request_full_weather_time, request_full_weather_interval


# @pytest.mark.parametrize("mock_config", [mock_config_detail_true, mock_config_detail_false])
# @pytest.mark.parametrize("mock_requests", [mock_request_401, mock_request_404, mock_request_200])
# def test_full_weather(request_full_weather, mock_config, mock_requests):
#     result = weather.get_weather_forecast(request_full_weather)
#     assert type(result) == str
#     json_result = json.loads(result)
#     assert type(json_result["speech"]["text"]) == str
#     assert json_result["speech"]["text"] is not ""

# @pytest.mark.parametrize("input_data", [mock_config_detail_true, mock_config_detail_false])
# @pytest.mark.parametrize("config", ["test_config_parser_console.ini", "test_config_parser_nlu.ini", "test_config_parser_rhasspy.ini"])
# def test_get_request_console(input_data, "test_config_parser_console.ini"):
#     pass
#
#
# def test_get_request_nlu(input_data, "test_config_parser_nlu.ini"):
#     pass

@pytest.mark.parametrize("input_key", ["request_weather_full_day", "request_weather_full_time", "request_weather_full_interval"])
@pytest.mark.parametrize("import_data", ["rhasspy_intent", "nlu_intent", "console_args"])
def test_get_request_rhasspy_full(input_key, import_data):
    input_data = intent.intents[import_data][input_key]
    config = None
    if import_data == "rhasspy_intent":
        input_data = json.loads(intent.intents[import_data][input_key])
        config = "test_config_parser_rhasspy.ini"
    elif import_data == "nlu_intent":
        config = "test_config_parser_nlu.ini"
    elif import_data == "console_args":
        config = "test_config_parser_console.ini"
    try:
        result = weather.get_request(input_data, config)
    except WeatherError as e:
        assert e.error_code == ErrorCode.PAST_WEATHER_ERROR
        result = e
    if type(result) == WeatherRequest:
        assert result.forecast_type == ForecastType.FULL
        assert result.request_date == datetime.date.today()
        if result.start_time is None:
            assert result.grain == Grain.DAY
            assert result.date_type == DateType.FIXED
        else:
            assert result.grain == Grain.HOUR
            assert result.time_specified != ''
            if result.start_time <= datetime.datetime.now().time():
                pass
            if result.end_time is None:
                assert result.date_type == DateType.FIXED
            else:
                assert result.date_type == DateType.INTERVAL
