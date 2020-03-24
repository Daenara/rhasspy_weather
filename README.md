# rhasspy Weather

## General
A python script that can make rhasspy voice assistant tell the weather. The output of the script is in German and so far it only works with the German rhasspy profile.

## Found a bug?
Just open an issue and supply me with the sentence that produced the bug. 

## Requirements
* python3
* [rhasspy](https://rhasspy.readthedocs.io/en/latest/) (Tested with 2.4.19 but should work with any version that can run custom commands)
* [suntime](https://pypi.org/project/suntime/)
* [open weather map api key](https://home.openweathermap.org/api_keys)

## Setup
I personally have created a folder called "custom_commands" in my rhasspy profile folder, put a custom_commands.py in there and made a subfolder there holding the contents of this repositery. The setup for a custom command in rhasspy 2.4 is described [here](https://rhasspy.readthedocs.io/en/latest/intent-handling/#command).

custom_commands.py
```
#!/usr/bin/python3

import sys
import json
from rhasspy_weather.rhasspy_weather import Weather

def speech(text):
    global o
    o["speech"] = {"text": text}

# get json from stdin and load into python dict
o = json.loads(sys.stdin.read())

intent = o["intent"]["name"]

if intent.startswith("GetWeatherForecast"):
    weather = Weather()
    speech(weather.get_weather_forecast(o))

# convert dict to json and print to stdout
print(json.dumps(o))
```

Replace the api key in rhasspy_weather.py for your own and change any other values you like. If "detail" is true and you querry the weather, temperature and so on for a full day it will read a much more detailed weather report that splits the day into morning, midday, noon and so on.

Other than the scripts you will need the intents. Here are mine (changes might break the scripts so please only change things if you know what you are doing):

sentences.ini
```
[GetWeatherForecast]
day = (heute|morgen|übermorgen|[am:] ($rhasspy/days|((0..31) $rhasspy/months)))
time = [((früh:morgen)|vormittag|mittag|nachmittag|abend|nacht|[um:] (0..24) [uhr:] [(0..59)])]
wie (ist|wird) das wetter <day> {when_day} <time> {when_time}
wie (ist|wird) <day> {when_day} <time> {when_time} das wetter

[GetWeatherForecastItem]
brauche ich <GetWeatherForecast.day> {when_day} [(eine|einen|ein)] {article} ($weather_items) {item}

[GetWeatherForecastCondition]
gibt es <GetWeatherForecast.day> {when_day} (regen|schnee) {condition}
scheint <GetWeatherForecast.day> {when_day} die (sonne) {condition}
(stürmt|schneit|regnet) {condition} es <GetWeatherForecast.day> {when_day}

[GetWeatherForecastTemperature]
(ist|wird) es <GetWeatherForecast.day> {when_day} (warm|kalt) {temperature}
wie (warm|kalt) {temperature} (ist|wird) es <GetWeatherForecast.day> {when_day}
was ist die temperatur am <GetWeatherForecast.day> {when_day}
```

slots
```
{
    "weather_item": [
        "kaputze",
        "regenmantel",
        "paar stiefel",
        "stiefel",
        "schirm",
        "winterjacke",
        "sandalen",
        "hut",
        "kappe",
        "sonnenschirm",
        "handschuhe",
        "schal",
        "gummistiefel",
        "sonnencreme",
        "mütze",
        "paar lange unterhosen",
        "winterstiefel",
        "sonnenhut",
        "regenschirm",
        "sonnenbrille",
        "paar sandalen",
        "paar gummistiefel",
        "paar handschuhe",
        "lange unterhose",
        "mantel",
        "halbschuhe",
        "paar halbschuhe",
        "paar winterstiefel"
    ],
    "weather_items": [
        "kaputze",
        "regenmantel",
        "paar stiefel",
        "stiefel",
        "schirm",
        "winterjacke",
        "sandalen",
        "hut",
        "kappe",
        "sonnenschirm",
        "handschuhe",
        "schal",
        "gummistiefel",
        "sonnencreme",
        "mütze",
        "paar lange unterhosen",
        "winterstiefel",
        "sonnenhut",
        "regenschirm",
        "sonnenbrille",
        "paar sandalen",
        "paar gummistiefel",
        "paar handschuhe",
        "lange unterhose",
        "mantel",
        "halbschuhe",
        "paar halbschuhe",
        "paar winterstiefel"
    ]
}
```

## Usage
If everything is set up you can querry the weather from rhasspy with sentenses like
 * Wie wird das Wetter morgen abend?
 * Brauche ich heute einen Regenschirm?
 * Wird es am 31. März kalt?
 
 ## Functionality
 The weather logic is quite big and can answer questions about the weather condition or temperature, the complete weather report and the neccesserity of some items. Date and time can be specified and so can the location.
 
 The rhasspy_weather parser can do a bit less right now because the location is not implemented. To balance that out rhasspy_weather knows quite a few items the logic did not learn so far.
 
 ## TODO
 * add location support
 * add config file
 * make daily times in rhasspy_weather.py fit those in weather_logic.py (and use the logic already there to output the weather)
 * move remaining slots from the sentences.ini to the slots
 * clean up and add to the sentences
 * add in new items to weather_logic.py
 * clean up code
