# rhasspy Weather

## General
A python script that can make rhasspy voice assistant tell the weather. The output of the script is in German and so far it only works with the German rhasspy profile.

## Found a bug?
Just open an issue and supply me with the sentence that produced the bug. 

## Requirements
* python3
* [rhasspy](https://rhasspy.readthedocs.io/en/latest/) (Tested with 2.4.19 but should work with any version that can run custom commands)
* [pytz](https://pypi.org/project/pytz/) (seems to be included in rhasspy docker)
* [suntime](https://pypi.org/project/suntime/)
* [open weather map api key](https://home.openweathermap.org/api_keys)

## Setup
I personally have created a folder called "custom_commands" in my rhasspy profile folder, put a custom_commands.py in there and made a subfolder there holding the contents of this repository. The setup for a custom command in rhasspy 2.4 is described [here](https://rhasspy.readthedocs.io/en/latest/intent-handling/#command). It is important to note that rhasspy will only answer if forward_to_hass is true. If you don't use homeassistant then you need to figure out another way to read the answer. For rhasspy 2.4 you can call the /api/text-to-speech in the speech(text) function instead of adding to the dictionary. If you have rhasspy 2.5 running you can also use mqtt instead of the api to read out the answer.

<details>
<summary>custom_commands.py (click to expand)</summary>
<p>

```python
#!/usr/bin/python3

import sys
import json
import datetime
import pytz
import rhasspy_weather.rhasspy_weather as weather

import os
import logging

logging_format = '%(asctime)s - %(levelname)-5s - %(name)s.%(funcName)s[%(lineno)d]: %(message)s'
logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), 'output.log'), format=logging_format, datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)

def customTime(*args):
    converted = datetime.datetime.now(pytz.timezone('Europe/Berlin'))
    return converted.timetuple()

logging.Formatter.converter = customTime

log = logging.getLogger(__name__)

def exception_to_log(type, value, traceback):
    log.exception("Uncaught exception: ", exc_info=(type, value, traceback))

sys.excepthook = exception_to_log

def speech(text):
    global o
    o["speech"] = {"text": text}

log.info("Custom Script Started")
# get json from stdin and load into python dict
o = json.loads(sys.stdin.read())

intent = o["intent"]["name"]

if intent.startswith("GetWeatherForecast"):
    log.info("Detected Weather Intent")
    forecast = weather.get_weather_forecast(o)
    speech(forecast)

# convert dict to json and print to stdout
print(json.dumps(o))
```

</p>
</details>

You need a config file for the scripts to do anything. Either run the command script once after you added it or manually rename the "config.default" file to "config.ini" and edit it to your liking. 

Be sure to add your api key for OpenWeatherMap in, otherwise you will only get an error as output.
If "LevelOfDetail" is set to True and you query the weather, temperature and so on for a full day it will read a much more detailed weather report that splits the day into morning, midday, noon and so on.

Other than the scripts and the config you will need the intents. Here are mine (changes might break the scripts so please only change things if you know what you are doing):

<details>
<summary>sentences.ini (click to expand)</summary>
<p>

```
[GetWeatherForecast]
day = ($named_days|[am:] ($rhasspy/days|((0..31) $rhasspy/months))|in (0..7) Tagen)
time = ($named_times|[um:] (0..24) [Uhr:] [(0..59)]|in (einer Stunde|(2..100) Stunden))
location = [(Frankfurt|Berlin|Regensburg|London)]
wie (ist|wird) das wetter [<day> {when_day}] [<time> {when_time}] [in <location> {location}]
wie (ist|wird) [<day> {when_day}] [<time> {when_time}] das wetter [in <location> {location}]

[GetWeatherForecastItem]
brauche ich [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}] [(eine|einen|ein) {article}] $weather_items {item}

[GetWeatherForecastCondition]
gibt es [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}] $weather_condition {condition}
scheint [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}] die $weather_condition {condition}
$weather_condition {condition} es [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}]

[GetWeatherForecastTemperature]
(ist|wird) es [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}] (warm|kalt) {temperature}
wie (warm|kalt) {temperature} (ist|wird) es [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}]
was ist die temperatur [am <GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}]
```

</p>
</details>

<details>
<summary>Slots (click to expand)</summary>
<p>
    
```
{
    "named_days": [
        "übermorgen",
        "morgen",
        "heute"
    ],
    "named_times": [
        "nacht",
        "nachmittag",
        "vormittag",
        "früh",
        "morgen",
        "abend",
        "mittag"
    ],
    "weather_items": [
        "regenmantel",
        "hut",
        "kaputze",
        "paar gummistiefel",
        "sonnenhut",
        "sonnenschirm",
        "mütze",
        "sonnencreme",
        "regenschirm",
        "schirm",
        "paar lange unterhosen",
        "stiefel",
        "paar handschuhe",
        "lange unterhosen",
        "handschuhe",
        "mantel",
        "lange unterhose",
        "halbschuhe",
        "paar halbschuhe",
        "gummistiefel",
        "schal",
        "paar stiefel",
        "winterstiefel",
        "sonnenbrille",
        "winterjacke",
        "paar sandalen",
        "kappe",
        "paar winterstiefel",
        "sandalen"
    ],
    "weather_condition": [
        "regen",
        "schnee",
        "nebel",
        "wolken",
        "gewitter",
        "sonne",
        "wind",
        "stürmt:wind",
        "regnet:regen",
        "schneit:schnee"
    ]
}
```
    
</p>
</details>

## Usage
If everything is set up you can query the weather from rhasspy with sentences like
 * Wie wird das Wetter morgen abend?
 * Brauche ich heute einen Regenschirm?
 * Wird es am 31. März kalt?
 * Wie ist das Wetter heute?
 * Regnet es morgen in Berlin?
 
## Functionality
The weather logic is quite powerful and can answer questions about the weather condition or temperature, the complete weather report and the necessary of some items. Date and time can be specified and so can the location. The logic itself can even handle multiple queries at once if they are passed in the right format, it will then read everything in a row.

When using the weather logic with rhasspy it is less powerful because the sentences written for rhasspy and the parser just don't have that functionality (yet).

Multiple requests at the same time is not something I know how to implement with the rhasspy grammar and I do not see much need in it so it is not on my todo list even thought the logic could do it. 

On the other side there are a few items that can be queried for with rhasspy that the logic has not learned yet, so both sides aren't perfect.
 
 ## TODO
* [ ] **Rework the item system for requests**
    * [ ] add custom item class saving name, grammar information and condition type
        * [ ] properly format item for output
        * [ ] output conditions it can be useful in
    * [ ] write wrapper class to hold those items
        * [ ] find if item is in list
        * [ ] (maybe) list items by condition
        * [ ] export items to rhasspy slot program
    * [ ] while at it, add in new item types (there are types in my rhasspy slot the logic does not now and parts in the logic that rhasspy does not know)
* [ ] **(maybe) add a dict full of aliases for weather conditions to language files and import everything in it as rhasspy slot program as well as map those aliases to conditions (similar to named_days and named_times aliases)**
* [ ] **(maybe) export named_days, named_times and their aliases as slot program**
* [ ] **rewrite the logic for a detailed weather report (and remove the last hardcoded language stuff with that)**
* [ ] **add in logic for ConditionType.WIND**
    * [ ] add wind as an extra WeatherCondition
        * [ ] figure out a wind speed to severity conversion
        * [ ] figure out how to write a custom description for wind (owm does not do that for me) and translate that
        * [ ] add filter functionality to only add certain conditions to answers (I do not want to hear about a mild wind in my daily weather report)
    * [ ] define and use items that are useful for wind
    * [ ] make it possible to ask about wind condition
* [ ] **add output system to define how this script outputs**
    * [ ] rhasspy hass.io json (current way)
    * [ ] extended json (add in an output part to json containing the answer to the question as well as some information)
    * [ ] mqtt
    * [ ] rhasspy web api tts
* [ ] **clean up code**
    * [ ] remove all comments referencing snips
    * [ ] replace comments documenting functions with pydoc strings
    * [ ] add documentation for everything that has none
    * [X] figure out a way to have the config globally accessible without having to import it inside functions because it is not initialized otherwise
    * [ ] cleaning up imports in general
    * [X] move definition for warm and cold from language files to config file
    * [ ] find every not implemented feature that could be implemented (StatusCode.NOT_IMPLEMENTED_ERROR)
* [ ] **clean up on the rhasspy side of things**
     * [ ] clean up sentences for rhasspy and add some
     * [ ] offer an English translation for rhasspy sentences
* [ ] **add to this documentation**
    * [ ] table of content
    * [ ] file structure graph
    * [ ] rewrite most of the text
        * [ ] add better explanation for setup
        * [ ] add explanation of config
        * [ ] rewrite functionality part
