import datetime

from rhasspy_weather.data_types.config import get_config

from rhasspy_weather.utils.dt_utils import get_date_with_year


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

