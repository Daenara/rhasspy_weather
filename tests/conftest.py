import json
import os
from pathlib import Path

import pytest
import pytz

from rhasspy_weather.data_types.location import Location


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


class MockResponse:
    def __init__(self, response_type):
        if response_type == "error_401":
            self.__response = '{"cod":401, "message": "Invalid API key. Please see http://openweathermap.org/faq#error401 for more info."}'

    def json(self):
        return json.loads(self.__response)


@pytest.fixture()
def request_full_weather():
    return json.loads('{ "entities": [], "intent": {"confidence": 1, "name": "GetWeatherForecast"}, "raw_text": "wie '
                      'wird das wetter", "raw_tokens": ["wie", "wird", "das", "wetter"], "recognize_seconds": '
                      '0.08515081899531651, "slots": {}, "speech_confidence": 1, "text": "wie wird das wetter", '
                      '"tokens": ["wie", "wird", "das", "wetter"], "wakeword_id": null}')


@pytest.fixture
def mock_config_detail_true(monkeypatch):
    def mock_get_config(*args, **kwargs):
        return MockConfig(True, "rhasspy_intent", "console_json", "rhasspy.json", "german")

    from rhasspy_weather.data_types import config
    monkeypatch.setattr(config, "get_config", mock_get_config)


@pytest.fixture
def mock_config_detail_false(monkeypatch):
    def mock_get_config(*args, **kwargs):
        return MockConfig(False, "rhasspy_intent", "console_json", "rhasspy.json", "german")

    from rhasspy_weather.data_types import config
    monkeypatch.setattr(config, "get_config", mock_get_config)


@pytest.fixture
def mock_request_401(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse("error_401")

    import requests
    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture
def mock_request_404(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse("error_404")

    import requests
    monkeypatch.setattr(requests, "get", mock_get)
