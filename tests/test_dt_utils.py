import datetime

import pytest

from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.error import WeatherError, ErrorCode

from rhasspy_weather.utils.dt_utils import get_date_with_year, named_day_to_date, weekday_to_date, date_string_to_date, \
    named_time_to_time


def test_get_date_with_year(mock_config_detail_true):
    config = get_config()
    today = datetime.datetime.now(tz=config.timezone).date()

    test_1 = get_date_with_year(today.day - 1, today.month)
    assert test_1.day == today.day - 1
    assert test_1.month == today.month
    assert test_1.year == today.year + 1

    test_2 = get_date_with_year(today.day + 1, today.month)
    assert test_2.day == today.day + 1
    assert test_2.month == today.month
    assert test_2.year == today.year

    test_3 = get_date_with_year(today.day - 1, today.month, True)
    assert test_3.day == today.day - 1
    assert test_3.month == today.month
    assert test_3.year == today.year

    test_4 = get_date_with_year(today.day + 1, today.month, True)
    assert test_4.day == today.day + 1
    assert test_4.month == today.month
    assert test_4.year == today.year


def test_named_day_to_date(mock_config_detail_true):
    config = get_config()
    today = datetime.datetime.now(tz=config.timezone).date()
    for named_day in config.locale.named_days.keys():
        result = named_day_to_date(named_day)
        named_day_value = config.locale.named_days[named_day]
        if type(named_day_value) == int:
            offset = datetime.timedelta(named_day_value)
            assert today + offset == result
        elif type(named_day_value) == datetime.date:
            assert named_day_value == result

    for named_day in config.locale.named_days_synonyms.keys():
        result = named_day_to_date(named_day)
        named_day_value = config.locale.named_days[config.locale.named_days_synonyms[named_day]]
        if type(named_day_value) == int:
            offset = datetime.timedelta(named_day_value)
            assert today + offset == result
        elif type(named_day_value) == datetime.date:
            assert named_day_value == result

    with pytest.raises(WeatherError) as error:
        named_day_to_date("blah")
    assert type(error.value.error_code) == ErrorCode


def test_weekday_to_date(mock_config_detail_true):
    config = get_config()
    for weekday in config.locale.weekday_names:
        result = weekday_to_date(weekday)
        assert result.weekday() == config.locale.weekday_names.index(weekday)

    today = datetime.datetime.now(tz=config.timezone).date()
    assert weekday_to_date(config.locale.weekday_names[today.weekday()]) == today + datetime.timedelta(days=7)


def test_date_string_to_date(mock_config_detail_true):
    config = get_config()
    result = date_string_to_date("31 " + config.locale.month_names[4])
    assert result.day == 31
    assert result.month == 5

    result = date_string_to_date("31 5")
    assert result.day == 31
    assert result.month == 5

    result = date_string_to_date("31:05", ":")
    assert result.day == 31
    assert result.month == 5

    with pytest.raises(WeatherError) as error:
        date_string_to_date("45 01")
    assert type(error.value.error_code) == ErrorCode

    with pytest.raises(WeatherError) as error:
        date_string_to_date("13 15")
    assert type(error.value.error_code) == ErrorCode

    with pytest.raises(WeatherError) as error:
        date_string_to_date("14: 15 31")
    assert type(error.value.error_code) == ErrorCode


def test_named_time_to_time(mock_config_detail_true):
    config = get_config()
    for named_time in config.locale.named_times.keys():
        named_time_value = config.locale.named_times[named_time]
        assert named_time_value == named_time_to_time(named_time)

    for named_time in config.locale.named_times_synonyms.keys():
        named_time_value = config.locale.named_times[config.locale.named_times_synonyms[named_time]]
        assert named_time_value == named_time_to_time(named_time)

    with pytest.raises(WeatherError) as error:
        named_time_to_time("blah")
    assert type(error.value.error_code) == ErrorCode

