import json
import os
from pathlib import Path

import pytest
import pytz

from rhasspy_weather.data_types.location import Location
from tests.data.openweathermap_weather import MockResponse


class MockConfig:
    def __init__(self, detail, parser, output, output_template, locale):
        base_path = os.path.join(str(Path(__file__).parent.parent), "rhasspy_weather")
        self.__detail = detail
        name = "rhasspy_weather.parser." + parser
        self.__parser = __import__(name, fromlist=[''])
        name = "rhasspy_weather.output." + output
        self.__output = __import__(name, fromlist=[''])
        path = os.path.join(base_path, "output_templates", output_template)
        self.__output_template = open(path, 'r').read()
        name = "rhasspy_weather.languages." + locale
        self.__locale = __import__(name, fromlist=[''])

    @property
    def detail(self):
        return self.__detail

    @property
    def api(self):
        name = "rhasspy_weather.api." + "openweathermap"
        return __import__(name, fromlist=[''])

    @property
    def parser(self):
        return self.__parser

    @property
    def output(self):
        return self.__output

    @property
    def output_template(self):
        return self.__output_template

    @property
    def temperature_warm_from(self):
        return 20

    @property
    def temperature_cold_to(self):
        return 5

    @property
    def timezone(self):
        return pytz.timezone("Europe/Berlin")

    @property
    def units(self):
        return "metric"

    @property
    def locale(self):
        return self.__locale

    @property
    def location(self):
        return Location("Berlin")

    @property
    def api_key(self):
        return "test_config"

    @property
    def error(self):
        return False


@pytest.fixture
def request_full_weather():
    return json.loads('{ "entities": [], "intent": {"confidence": 1, "name": "GetWeatherForecast"}, "raw_text": "wie '
                      'wird das wetter", "raw_tokens": ["wie", "wird", "das", "wetter"], "recognize_seconds": '
                      '0.08515081899531651, "slots": {}, "speech_confidence": 1, "text": "wie wird das wetter", '
                      '"tokens": ["wie", "wird", "das", "wetter"], "wakeword_id": null}', ensure_ascii=False)


@pytest.fixture
def mock_config_detail_true(monkeypatch):
    def mock_get_config():
        from tests.conftest import MockConfig
        return MockConfig(True, "rhasspy_intent", "console", "rhasspy.json", "german")

    monkeypatch.setattr("rhasspy_weather.data_types.config.get_config.__code__", mock_get_config.__code__)


@pytest.fixture
def mock_config_detail_false(monkeypatch):
    def mock_get_config():
        from tests.conftest import MockConfig
        return MockConfig(False, "rhasspy_intent", "console", "rhasspy.json", "german")

    monkeypatch.setattr("rhasspy_weather.data_types.config.get_config.__code__", mock_get_config.__code__)


@pytest.fixture
def mock_request_401(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse("response_401")

    import requests
    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture
def mock_request_404(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse("response_404")

    import requests
    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture
def mock_request_200(monkeypatch):
    def mock_get(*args, **kwargs):
        data_input = [
            {"temp": 30, "f_temp": 29, "min_temp": 28, "max_temp": 31, "pressure": 1009, "humidity": 50, "weather_id": 500},
            {"temp": 25, "f_temp": 27, "min_temp": 23, "max_temp": 28, "pressure": 1006, "humidity": 58, "weather_id": 503},
            {"temp": 0, "f_temp": 3, "min_temp": -3, "max_temp": 5, "pressure": 1009, "humidity": 11, "weather_id": 601},
            {"temp": 5, "f_temp": 4, "min_temp": 3, "max_temp": 7, "pressure": 1015, "humidity": 20, "weather_id": 800},
            {"temp": 15, "f_temp": 18, "min_temp": 14, "max_temp": 17, "pressure": 1020, "humidity": 33, "weather_id": 800},
            {"temp": 18, "f_temp": 16, "min_temp": 17, "max_temp": 18, "pressure": 1019, "humidity": 35, "weather_id": 803}
        ]
        return MockResponse("response_404", data_input)

    import requests
    monkeypatch.setattr(requests, "get", mock_get)

