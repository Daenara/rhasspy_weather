import datetime
import json

weather_conditions = {
    200: ("Thunderstorm", "", "11d"),
    201: ("Thunderstorm", "", "11d"),
    202: ("Thunderstorm", "", "11d"),
    210: ("Thunderstorm", "", "11d"),
    211: ("Thunderstorm", "", "11d"),
    212: ("Thunderstorm", "", "11d"),
    221: ("Thunderstorm", "", "11d"),
    230: ("Thunderstorm", "", "11d"),
    231: ("Thunderstorm", "", "11d"),
    232: ("Thunderstorm", "", "11d"),
    300: ("Drizzle", "", "09d"),
    301: ("Drizzle", "", "09d"),
    302: ("Drizzle", "", "09d"),
    310: ("Drizzle", "", "09d"),
    311: ("Drizzle", "", "09d"),
    312: ("Drizzle", "", "09d"),
    313: ("Drizzle", "", "09d"),
    314: ("Drizzle", "", "09d"),
    321: ("Drizzle", "", "09d"),
    500: ("Rain", "Leichter Regen", "10d"),
    501: ("Rain", "Mäßiger Regen", "10d"),
    502: ("Rain", "", "10d"),
    503: ("Rain", "", "10d"),
    504: ("Rain", "", "10d"),
    511: ("Rain", "", "13d"),
    520: ("Rain", "", "09d"),
    521: ("Rain", "", "09d"),
    522: ("Rain", "", "09d"),
    531: ("Rain", "", "09d"),
    600: ("Snow", "", "13d"),
    601: ("Snow", "", "13d"),
    602: ("Snow", "", "13d"),
    611: ("Snow", "", "13d"),
    612: ("Snow", "", "13d"),
    613: ("Snow", "", "13d"),
    615: ("Snow", "", "13d"),
    616: ("Snow", "", "13d"),
    620: ("Snow", "", "13d"),
    621: ("Snow", "", "13d"),
    622: ("Snow", "", "13d"),
    701: ("Mist", "", "50d"),
    711: ("Smoke", "", "50d"),
    721: ("Haze", "", "50d"),
    731: ("Dust", "", "50d"),
    741: ("Fog", "", "50d"),
    751: ("Sand", "", "50d"),
    761: ("Dust", "", "50d"),
    762: ("Ash", "", "50d"),
    771: ("Squall", "", "50d"),
    781: ("Tornado", "", "50d"),
    800: ("Clear", "Klarer Himmel", "01d"),
    801: ("Clouds", "Ein paar Wolken", "02d"),
    802: ("Clouds", "Mäßig bewölkt", "03d"),
    803: ("Clouds", "Überwiegend bewölkt", "04d"),
    804: ("Clouds", "Bedeckt", "04d")
}

weather_data = {
    "response_401": '{"cod":401, "message": "Invalid API key. Please see http://openweathermap.org/faq#error401 for more info."}',
    "response_404": '{"cod":"404","message":"city not found"}',
    "response_200": '{"cod":"200","message":0,"cnt":{cnt}},"city":{city},list:{list}}',
    "city": {
        "frankfurt": '{"id":2925533,"name":"Frankfurt am Main","coord":{"lat":50.1167,"lon":8.6833},"country":"DE","population":650000,"timezone":7200,"sunrise":1597810874,"sunset":1597862205}',
    },
    "list": '{"dt":{dt},"main":{"temp":{temp},"feels_like":{f_temp},"temp_min":{min_temp},"temp_max":{max_temp},"pressure":{pressure},"sea_level":1009,"grnd_level":996,"humidity":{humidity},"temp_kf":0.7},"weather":[{"id":{weather_id},"main":"{weather_condition}","description":"{weather_description}","icon":"{weather_icon}"}],"clouds":{"all": 83},"wind":{"speed": 1.6,"deg":168},"visibility":10000,"pop":0,"sys":{"pod":"d"},"dt_txt":"{dt_txt}"}'
}

times = [datetime.time(0,0), datetime.time(3,0), datetime.time(6,0), datetime.time(9,0), datetime.time(12,0), datetime.time(15,0), datetime.time(18,0), datetime.time(21,0)]


def build_weather_list(input_list, date, time):
    output_list = []
    date_and_time = datetime.datetime.combine(date, time)
    for entry in input_list:
        weather_entry = weather_data["list"]
        for key, value in entry.items():
            weather_entry = weather_entry.replace("{" + key + "}", str(value))
        weather_entry = weather_entry.replace("{dt}", str(int(date_and_time.timestamp()))).replace("{dt_txt}", str(date_and_time))
        weather_condition = weather_conditions[entry["weather_id"]]
        weather_entry = weather_entry.replace("{weather_condition}", weather_condition[0]).replace("{weather_description}", weather_condition[1]).replace("{weather_icon}", weather_condition[2])
        output_list.append(weather_entry)
        date_and_time = date_and_time + datetime.timedelta(hours=3)
    return output_list


class MockResponse:
    def __init__(self, response_type, data_input=None, city=None, start_date=None, start_time=None):
        if response_type == "response_200" and data_input is not None:
            if city is None or city not in weather_data["city"]:
                city = "frankfurt"
            if start_date is None:
                start_date = datetime.date.today()
            if start_time is None:
                start_time = times[0]
                for i in range(0, len(times)-1):
                    if times[i] < datetime.datetime.now().time() < times[i + 1]:
                        start_time = times[i+1]
                        break

            output_list = build_weather_list(data_input, start_date, start_time)
            response = weather_data["response_200"]
            response = response.replace("{city}", city)
            response = response.replace("{list}", str(output_list))
            response = response.replace("{cnt}", str(len(output_list)))
            self.__response = response
        else:
            self.__response = weather_data[response_type]

    def json(self):
        return json.loads(self.__response)

