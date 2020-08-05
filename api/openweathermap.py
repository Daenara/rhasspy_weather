import datetime
import logging

import requests

from rhasspy_weather.data_types.config import get_config
from rhasspy_weather.data_types.condition import WeatherCondition, ConditionType
from rhasspy_weather.data_types.forecast import WeatherForecast
from rhasspy_weather.data_types.status import StatusCode

log = logging.getLogger(__name__)


def get_weather(location):
    """gets weather from openweathermap API and parses it

    Parameters:
    weather_api_key : str
        API key for openweathermap
    weather_forecast: WeatherForecast
        
    """
    log.debug("parsing weather from openweathermap")
    config = get_config()
    weather_forecast = WeatherForecast()

    if hasattr(location, "lat") and hasattr(location, "lon"):
        url_location = "lat={lat}&lon={lon}".format(lat=location.lat, lon=location.lon)
    elif hasattr(location, "zipcode") and hasattr(location, "country_code"):
        url_location = "zip={zip},{country_code}".format(zip=location.zipcode, country_code=location.country_code)
    else:
        url_location = "q={city_name}".format(city_name=location.city)
    forecast_url = "http://api.openweathermap.org/data/2.5/forecast?{location}&APPID={api_key}&units={units}&lang={language_code}".format(location=url_location, api_key=config.api_key, units=config.units, language_code=config.locale.language_code)
    try:
        response = requests.get(forecast_url)
        response = response.json()

        if str(response["cod"]) == "401":
            weather_forecast.status.set_status(StatusCode.API_ERROR)
            return weather_forecast
        elif str(response["cod"]) == "429":
            weather_forecast.status.set_status(StatusCode.API_TIMEOUT_ERROR)
            return weather_forecast
        elif str(response["cod"]) == "404":
            weather_forecast.status.set_status(StatusCode.LOCATION_ERROR)
            return weather_forecast

        # Parse the output of Open Weather Map's forecast endpoint
        if not (hasattr(location, "lat") and hasattr(location, "lon")):
            location.set_lat_and_lon(response["city"]["coord"]["lat"], response["city"]["coord"]["lon"])
        weather_forecast.calculate_sunrise_and_sunset(location.lat, location.lon)
        forecasts = {}
        for x in response["list"]:
            if str(datetime.date.fromtimestamp(x["dt"])) not in forecasts:
                forecasts[str(datetime.date.fromtimestamp(x["dt"]))] = \
                    list(filter(lambda forecast: datetime.date.fromtimestamp(forecast["dt"]) == datetime.date.fromtimestamp(x["dt"]), response["list"]))

        for key, forecast in forecasts.items():
            condition_list = []
            weather_condition = [x["weather"][0]["main"] for x in forecast]
            weather_description = [x["weather"][0]["description"] for x in forecast]
            weather_id = [x["weather"][0]["id"] for x in forecast]
            for x in range(len(weather_condition)):
                temp_condition = WeatherCondition(__get_severity_from_open_weather_map_id(weather_id[x]), weather_description[x], __get_condition_type(weather_id[x]))
                condition_list.append(temp_condition)
            tmp = WeatherForecast.WeatherAtDate(datetime.datetime.strptime(key, "%Y-%m-%d").date())
            tmp.parse_weather(
                [datetime.datetime.strptime(x, "%H:%M:%S").time() for x in [x["dt_txt"].split(" ")[1] for x in forecast]],
                [x["main"]["temp"] for x in forecast], condition_list, [x["main"]["pressure"] for x in forecast],
                [x["main"]["humidity"] for x in forecast],
                [x["wind"]["speed"] for x in forecast],
                [x["wind"]["deg"] for x in forecast]
            )
            weather_forecast.forecast.append(tmp)
    except (requests.exceptions.ConnectionError, ValueError):
        weather_forecast.status.set_status(StatusCode.NO_NETWORK_ERROR)
    return weather_forecast


# parses the weather condition into my own format (WeatherCondition)
def __get_severity_from_open_weather_map_id(owm_id):
    switcher = {
        # owm_id -> intensity
        210: 0,  # light thunderstorm
        211: 1,  # thunderstorm
        230: 3,  # thunderstorm with light drizzle
        231: 4,  # thunderstorm with drizzle
        232: 5,  # thunderstorm with heavy drizzle
        200: 6,  # thunderstorm with light rain
        201: 7,  # thunderstorm with rain
        202: 8,  # thunderstorm with heavy rain
        212: 9,  # heavy thunderstorm
        221: 10, # ragged thunderstorm

        300: 0,  # light drizzle
        301: 1,  # drizzle
        321: 1,  # shower drizzle
        302: 2,  # heavy intensity drizzle
        310: 3,  # light intensity drizzle rain
        311: 4,  # drizzle rain
        312: 5,  # heavy intensity drizzle rain
        313: 6,  # shower rain and drizzle
        314: 7,  # heavy shower rain and drizzle

        500: 0,  # light rain
        520: 0,  # light intensity shower rain
        501: 1,  # moderate rain
        521: 1,  # shower rain
        511: 1,  # freezing rain
        502: 2,  # heavy intensity rain
        522: 2,  # heavy intensity shower rain
        503: 3,  # very heavy rain
        531: 3,  # ragged shower rain
        504: 4,  # extreme rain

        600: 0,  # light snow
        620: 0,  # light shower snow
        612: 0,  # light shower sleet
        615: 1,  # light rain and snow
        601: 1,  # snow
        621: 1,  # shower snow
        611: 1,  # sleet
        613: 1,  # shower sleet
        616: 2,  # rain and snow
        602: 2,  # heavy snow
        622: 2,  # heavy shower snow

        800: 0,  # clear sky
        801: 1,  # few clouds: 11-25%
        802: 2,  # scattered clouds: 25-50%
        803: 3,  # broken clouds: 51-84%
        804: 4   # overcast clouds: 85-100%
    }
    
    return switcher.get(owm_id, 0)


def __get_condition_type(owm_id):
    first_digit = int(str(owm_id)[0])
    if first_digit == 2:
        return ConditionType.THUNDERSTORM
    elif first_digit == 3 or first_digit == 5:
        return ConditionType.RAIN
    elif first_digit == 6:
        return ConditionType.SNOW
    elif owm_id == 800:
        return ConditionType.CLEAR
    elif first_digit == 8:
        return ConditionType.CLOUDS
    elif owm_id == 701 or owm_id == 741:
        return ConditionType.MIST
    else:
        return ConditionType.MISC
