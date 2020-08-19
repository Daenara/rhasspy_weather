import json

import pytest
from rhasspy_weather import weather


@pytest.fixture()
def request_full_weather():
    return json.loads('{ "entities": [], "intent": {"confidence": 1, "name": "GetWeatherForecast"}, "raw_text": "wie '
                      'wird das wetter", "raw_tokens": ["wie", "wird", "das", "wetter"], "recognize_seconds": '
                      '0.08515081899531651, "slots": {}, "speech_confidence": 1, "text": "wie wird das wetter", '
                      '"tokens": ["wie", "wird", "das", "wetter"], "wakeword_id": null}')


def test_full_weather(request_full_weather):
    result = weather.get_weather_forecast(request_full_weather)
    assert type(result) == str
    json_result = json.loads(result)
    assert type(json_result["speech"]["text"]) == str
    assert json_result["speech"]["text"] is not ""
