import pytest

from rhasspy_weather.utils.utils import normal_round, remove_excessive_whitespaces, format_string


@pytest.mark.parametrize("test_data", [(0.5, 1), (0.4, 0), (0.6, 1), (0, 0), (1, 1)])
def test_normal_round(test_data):
    assert normal_round(test_data[0]) == test_data[1]


@pytest.mark.parametrize("test_data", [("Ich     habe   zu     viele      Leerzeichen.", 4), ("          ", 1), ("Ich habe kein Leerzeichen zu viel.", 5)])
def test_remove_excessive_whitespaces(test_data):
    assert remove_excessive_whitespaces(test_data[0]).count(" ") == test_data[1]


@pytest.mark.parametrize("test_data", [("Ich bin ein Testsatz..  .", "Ich bin ein Testsatz."), ("ich bin ein Testsatz.", "Ich bin ein Testsatz."), ("Ich bin ein Testsatz... Ich auch .", "Ich bin ein Testsatz. Ich auch.")])
def test_format_string(test_data):
    assert format_string(test_data[0]) == test_data[1]
