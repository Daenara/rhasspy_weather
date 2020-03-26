import requests
import datetime
from rhasspy_weather.forecast import WeatherForecast
from rhasspy_weather.helpers import WeatherCondition, Location
from rhasspy_weather.status import StatusCode

import logging

log = logging.getLogger(__name__)

def get_weather(api_key, location, units, timezone):
    """gets weather from openweathermap API and parses it
    Returns 0 is everything worked, if not returns the error code
    Parameters:
    weather_api_key : str
        API key for openweathermap
    weather_forecast: WeatherForecast
        
    """
    log.debug("parsing weather from openweathermap")
    weather_forecast = WeatherForecast(timezone)

    if hasattr(location, "lat") and hasattr(location, "lon"):
        url_location = "lat={lat}&lon={lon}".format(lat=location.lat, lon=location.lon)
    elif hasattr(location, "zipcode") and hasattr(location, "country"):
        url_location = "zip={zip},{country_code}".format(zip=location.zipcode, country_code=location.country)
    else:
        url_location = "q={city_name}".format(city_name=location.name)
    forecast_url = "http://api.openweathermap.org/data/2.5/forecast?{location}&APPID={api_key}&units={units}&lang=de".format(\
        location=url_location, api_key=api_key, units=units)
    try:
        response = requests.get(forecast_url)
        response = response.json()

        if str(response["cod"]) == "401":
            weather_forecast.status.set_status(StatusCode.API_ERROR) # Error: something went wrong with the api call
            return weather_forecast
        elif str(response["cod"]) == "429":
            weather_forecast.status.set_status(StatusCode.API_TIMEOUT_ERROR) # Error: request limit exceeded
            return weather_forecast
        elif str(response["cod"]) == "404":
            weather_forecast.status.set_status(StatusCode.LOCATION_ERROR) # Error: location not found
            return weather_forecast
            
        # Parse the output of Open Weather Map's forecast endpoint
        if not (hasattr(location, "lat") and hasattr(location, "lon")):
            location.set_lat_and_lon(response["city"]["coord"]["lat"], response["city"]["coord"]["lon"])
        weather_forecast.calculate_sunrise_and_sunset(location)
        forecasts = {}
        for x in response["list"]:
            if str(datetime.date.fromtimestamp(x["dt"])) not in forecasts:
                forecasts[str(datetime.date.fromtimestamp(x["dt"]))] = \
                    list(filter(lambda forecast: datetime.date.fromtimestamp(forecast["dt"]) == datetime.date.fromtimestamp(x["dt"]), response["list"]))
                
        for key,forecast in forecasts.items():
            condition_list = []
            weather_condition = [x["weather"][0]["main"] for x in forecast]
            weather_description = [x["weather"][0]["description"] for x in forecast]
            weather_id = [x["weather"][0]["id"] for x in forecast]
            for x in range(len(weather_condition)):
                temp_condition = WeatherCondition(__get_severity_from_open_weather_map_id(weather_id[x]), weather_description[x], weather_condition[x])
                condition_list.append(temp_condition)
            tmp = WeatherForecast.WeatherAtDate(datetime.datetime.strptime(key, "%Y-%m-%d").date())
            tmp.parse_weather([datetime.datetime.strptime(x, "%H:%M:%S").time() for x in [x["dt_txt"].split(" ")[1] for x in forecast]],\
               [x["main"]["temp"] for x in forecast], condition_list, [x["main"]["pressure"] for x in forecast],[x["main"]["humidity"] for x in forecast],\
               [x["wind"]["speed"] for x in forecast],[x["wind"]["deg"] for x in forecast])
            weather_forecast.forecast.append(tmp)
    except (requests.exceptions.ConnectionError, ValueError):
        forecast.status.set_status(NO_NETWORK_ERROR) # Error: No internet connection
    return weather_forecast
        
# parses the weather condition into my own format (WeatherConditon)
def __get_severity_from_open_weather_map_id(id):
    if id == 210: return 0 # light thunderstorm
    if id == 211: return 1 # thunderstorm
    if id == 230: return 3 # thunderstorm with light drizzle
    if id == 231: return 4 # thunderstorm with drizzle
    if id == 232: return 5 # thunderstorm with heavy drizzle
    if id == 200: return 6 # thunderstorm with light rain
    if id == 201: return 7 # thunderstorm with rain
    if id == 202: return 8 # thunderstorm with heavy rain
    if id == 212: return 9 # heavy thunderstorm
    if id == 221: return 10 # ragged thunderstorm

    if id == 300: return 0 # light drizzle
    if id == 301: return 1 # drizzle
    if id == 321: return 1 # shower drizzle
    if id == 302: return 2 # heavy intensity drizzle
    if id == 310: return 3 # light intensity drizzle rain
    if id == 311: return 4 # drizzle rain
    if id == 312: return 5 # heavy intensity drizzle rain
    if id == 313: return 6 # shower rain and drizzle
    if id == 314: return 7 # heavy shower rain and drizzle

    if id == 500: return 0 # light rain
    if id == 520: return 0 # light intensity shower rain
    if id == 501: return 1 # moderate rain
    if id == 521: return 1 # shower rain
    if id == 511: return 1 # freezing rain
    if id == 502: return 2 # heavy intensity rain
    if id == 522: return 2 # heavy intensity shower rain
    if id == 503: return 3 # very heavy rain
    if id == 531: return 3 # ragged shower rain
    if id == 504: return 4 # extreme rain

    if id == 600: return 0 # light snow
    if id == 620: return 0 # light shower snow
    if id == 612: return 0 # light shower sleet
    if id == 615: return 1 # light rain and snow
    if id == 601: return 1 # snow
    if id == 621: return 1 # shower snow
    if id == 611: return 1 # sleet
    if id == 613: return 1 # shower sleet
    if id == 616: return 2 # rain and snow
    if id == 602: return 2 # heavy snow
    if id == 622: return 2 # heavy shower snow

    if id == 801: return 0 # few clouds: 11-25%
    if id == 802: return 1 # scattered clouds: 25-50%
    if id == 803: return 2 # broken clouds: 51-84%
    if id == 804: return 3 # overcast clouds: 85-100%
   
    return 0