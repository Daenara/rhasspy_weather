import json

import pytest

from rhasspy_weather import weather
from tests.conftest import mock_config_detail_true, mock_config_detail_false, mock_request_401, mock_request_404


@pytest.mark.parametrize("mock_config", [mock_config_detail_true, mock_config_detail_false])
@pytest.mark.parametrize("mock_requests", [mock_request_401, mock_request_404])
def test_full_weather(request_full_weather, mock_config, mock_requests):
    result = weather.get_weather_forecast(request_full_weather)
    assert type(result) == str
    json_result = json.loads(result)
    assert type(json_result["speech"]["text"]) == str
    assert json_result["speech"]["text"] is not ""
