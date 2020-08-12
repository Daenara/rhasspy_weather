# rhasspy Weather

A python script that can make rhasspy voice assistant tell the weather.

## Found a bug?
Just open an issue and supply me with the sentence that produced the bug. 

## Table of Contents
* [Setup](#setup)
    * [custom_command script](#custom_command-script)
    * [sentences and slots](#setting-up-sentences-and-slots)
    * [config file](#config-file)
* [Usage](#usage)
* [Development](#development)
    * [Project Structure](#project-structure)
    * [What not to do](#what-not-to-do)
* [TODO](#todo)

## Setup
The whole setup procedure described was only tested on rhasspy 2.4. If you want to set it up on rhasspy 2.5 this might not work anymore.

### Requirements
* python3
* [rhasspy](https://rhasspy.readthedocs.io/en/latest/) (Tested with 2.4.19, should work with any version that can run custom commands)
* [pytz](https://pypi.org/project/pytz/) (seems to be included in rhasspy docker)
* [paho-mqtt](https://pypi.org/project/paho-mqtt/) (seems to be included in rhasspy docker, only needed for mqtt answer)
* [suntime](https://pypi.org/project/suntime/) (will be installed when missing)
* [dateutil](https://pypi.org/project/python-dateutil/) (will be installed when missing)
* [open weather map api key](https://home.openweathermap.org/api_keys)

### custom_command script
If you have not already set up a custom_command script for something else you need to set this up. Create a folder 
called *"custom_command"* in your rhasspy profile folder.

In this folder create a file called *"custom_commands.py"* and paste the code from below in there.

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
    o["rhasspy_weather"] = forecast

# convert dict to json and print to stdout
print(json.dumps(o))
```

</p>
</details>

Now you need to make rhasspy call that file to handle intents. To do so edit your profile.json so it contains the following.

The forward_to_hass setting has to be true, even if you don't use it because otherwise the custom command script I provide will not work.
```
{
    "handle": {
        "command": {
            "program": "$RHASSPY_PROFILE_DIR/custom_command/custom_commands.py"
        },
        "system": "command",
        "forward_to_hass": true
    },
    ... # the rest of your profile.json (make sure to not include this line)
}
```

### Setting up sentences and slots
Now we need to get rhasspy to actually recognize our intents. For that we will need to add the sentences to sentences.ini and also add the slots used in those.

#### Sentences
Copy the sentences below to your sentences.ini via the web gui. You can add to those or edit them but make sure the slots in the curly brackets {} stay the same.

You need to expand/edit the locations in the line *"location = [(Frankfurt|Berlin|Regensburg|London)]"* to something useful for you.

<details>
<summary>German Sentences (click to expand)</summary>
<p>

```
[GetWeatherForecast]
day = ($rhasspy_weather_slots/named_days|[am:] ($rhasspy/days|((0..31) $rhasspy/months))|in (0..7) Tagen)
time = ($rhasspy_weather_slots/named_times|[um:] (0..24) [Uhr:] [(0..59)]|in (einer Stunde|(2..100) Stunden))
location = [(Frankfurt|Berlin|Regensburg|London)]
wie (ist|wird) das wetter [<day> {when_day}] [<time> {when_time}] [in <location> {location}]
wie (ist|wird) [<day> {when_day}] [<time> {when_time}] das wetter [in <location> {location}]

[GetWeatherForecastItem]
brauche ich [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}] [(eine|einen|ein)] $rhasspy_weather_slots/items {item}

[GetWeatherForecastCondition]
gibt es [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}] $rhasspy_weather_slots/conditions {condition}
scheint [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}] die $rhasspy_weather_slots/conditions {condition}
$rhasspy_weather_slots/conditions {condition} es [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}]

[GetWeatherForecastTemperature]
(ist|wird) es [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}] $rhasspy_weather_slots/temperatures {temperature}
wie $rhasspy_weather_slots/temperatures {temperature} (ist|wird) es [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}]
was ist die temperatur [am <GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [in <GetWeatherForecast.location> {location}]
```

</p>
</details>

<details>
<summary>English Sentences (click to expand)</summary>
<p>

```
[GetWeatherForecast]
day = ($rhasspy_weather_slots/named_days|[on:] ($rhasspy/days|((0..31) $rhasspy/months))|in (0..7) days)
time = ($rhasspy_weather_slots/named_times|[at:] (0..24) [Uhr:] [(0..59)]|in (one hour|(2..100) hours))
location = [(Frankfurt|Berlin|Regensburg|London)]

(how|what|whats) (is|will) [the] weather [(be|going to be)] [<day> {when_day}] [<time> {when_time}] [(in|at) <location> {location}]
(how|what|whats) (is|will) [the] weather [(in|at) <location> {location}] [(be|going to be)] [<day> {when_day}] [<time> {when_time}]
(how|what|whats) (is|will) [<day> {when_day}] [<time> {when_time}] [the] weather [(be|going to be)] [(in|at) <location> {location}]


[GetWeatherForecastItem]
do (I|we|you) (need|have to take|have to bring|need to wear|need to take) [(a|an|some|any|one|the)] $rhasspy_weather_slots/items {item} [(in|at) <GetWeatherForecast.location> {location}] [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}]
do (I|we|you) (need|have to take|have to bring|need to wear|need to take) [(a|an|some|any|one|the)] $rhasspy_weather_slots/items {item} [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [(in|at) <GetWeatherForecast.location> {location}]

[GetWeatherForecastCondition]
(does it|is it|will it|will it be|will there be|is it going to|is there going to be) [(a|the)] $rhasspy_weather_slots/conditions {condition} [(in|at) <GetWeatherForecast.location> {location}] [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}]


[GetWeatherForecastTemperature]
(will it be|is it going to be) $rhasspy_weather_slots/temperatures {temperature} [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [(in|at) <GetWeatherForecast.location> {location}] 
how $rhasspy_weather_slots/temperatures {temperature} (is it|will it be|is it going to be) [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [(in|at) <GetWeatherForecast.location> {location}]
what is the temperature [<GetWeatherForecast.day> {when_day}] [<GetWeatherForecast.time> {when_time}] [(in|at) <GetWeatherForecast.location> {location}]
```

Thanks to [ulno](https://github.com/ulno/cli_weather) for his English sentences which are way better than mine were.
</p>
</details>

#### Slots
The slots are dynamically generated via rhasspy slot_programs. To set this up you need to create a folder *"slot_programs"* in your profile folder, navigate into the folder on a linux console and then create a symlink to the slot_programs folder that comes with this script.

```
ln -s ../custom_command/rhasspy_weather/slot_programs rhasspy_weather_slots
```

You can also manually copy the files in this folder into a subfolder! of slot_programs. The subfolder is important because the script loads modules from the main part of the script and navigates up to the profile folder from there. If anyone knows a way to get the path of the rhasspy profile without this crap, please let me know.

### Config file
The config file will be created once the script is run for the first time so no need to create it yourself.

```
[General]
api=openweathermap
parser=rhasspy_intent
output=hass_json
units=metric
timezone=Europe/Berlin
locale=german

[Weather]
temp_warm=20
temp_cold=5
level_of_detail=False

[Location]
city=Berlin
zipcode=
country_code=
lat=
lon=

[OpenWeatherMap]
api_key=

[mqtt]
address=
port=
user=
password=
topic=rhasspy_weather/response
```

* Valid values for api, parser, output and locale are the names of python files in the respective subfolder
* units can be either metric or imperial
* level_of_detail governs how detailed the answer is (true is hardcoded to german, pending rewrite)
* timezone values can be found [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
* temp_warm is the minimum temperature that is considered warm, temp_cold the maximum temperature to be considered cold
* zipcode and country_code will only be used if both are set, country_code refers to the two letter code of your country (e.g de)
* lat and lon will only be used if both are set
* be sure to input your owm api key, otherwise the script will not work
* the mqtt section will only be used when output is set to mqtt and can be removed if that is not the case


## Usage
If everything is set up you can query the weather:
### German:
* Wie wird das Wetter morgen abend?
* Brauche ich heute einen Regenschirm?
* Wird es am 31. März kalt?
* Wie ist das Wetter heute?
* Regnet es morgen in Berlin?
### English:
* How is the weather tomorrow in London?
* Do I need an umbrella?
* How cold is it tomorrow evening in London?
* Will it be warm on 31. March?
 
## Development
Some helpful things needed to know for development.

### Project Structure
```
custom_command
|--- rhasspy_weather                # this is actually in the github project
     |--- api                       # all weather api's go here
          |--- openweathermap.py    # default api
     |--- data_types                # basically tons of custom classes saving data
          |--- condition.py         
          |--- config.py            # config file is parsed here
          |--- forecast.py
          |--- interval.py
          |--- item.py
          |--- item_list.py
          |--- location.py
          |--- report.py
          |--- request.py           # this is what a parser outputs
          |--- status.py            # status and error handling
     |--- languages                 # language files go here
          |--- german.py
          |--- english.py
     |--- output
          |--- hass_json.py         # adds a speech part to the input json to be read by rhasspy
          |--- mqtt.py              # sends the answer per mqtt
     |--- parser                    # parsers go here
          |--- rhasspy_intent.py
     |--- slot_programs             # slot program generating rhasspy slots from language files
          |--- conditions
          |--- items
          |--- named_days
          |--- named_times
          |--- output.log           # output from slot_programs ends up here
          |--- temperatures
     |--- config.default
     |--- rhasspy_weather.py        # basically the main of the script (do only call from outside)
     |--- utils.py                  # misc functions that are used by more than one data_type
|--- custom_commands.py # the script rhasspy calls that uses this project
|--- output.log         # the file all logs land in (if my example custom_commands.py is used
```

### What not to do
#### call rhasspy_weather.py from inside the rhasspy_weather folder
Python3 imports are weird. If you call rhasspy_weather.py from inside the rhasspy_weather folder python will 
complain about the module rhasspy_weather not existing. Every fix I tried so far resulted in some kind of error. This
at least works if called from outside. Just make sure to always call from the folder the rhasspy_weather folder is in. I 
have not tried what happens if you go another folder up, probably import errors.

If you have/find a solution that works both from outside the folder (for custom_commands.py) as well as from inside 
the folder I am open for it.

#### call slot_programs from the slot_programs folder (slot_programs )
I used a bit of a hacky workaround to be able to import parts of the script from the slot_programs folder which results in
this quirky behaviour. Just always call from the folder that slot_programs (or the symlink to this) is in and it will work.

This is my hacky stuff. If someone has an idea how to get the folder of the current rhasspy profile in a better way, please tell me.
```
sys.path.append(os.path.abspath(os.path.join(os.path.join(os.path.join(os.path.dirname(__file__), '..'), '..'), "custom_command")))
```

## TODO
* [ ] **Rework the item system for requests**
    * [X] add custom item class saving name, grammar information and condition type
        * [X] properly format item for output
        * [X] output conditions it can be useful in
    * [X] write wrapper class to hold those items
        * [X] find if item is in list
        * [X] (maybe) list items by condition
        * [X] export items to rhasspy slot program
    * [X] while at it, add in new item types (there are types in my rhasspy slot the logic does not now and parts in the logic that rhasspy does not know)
    * [ ] actually use the new item system
        * [ ] replace function from language files
        * [ ] add in new condition types
        * [X] actually use ConditionType for conditions
        * [ ] add ConditionType.SUN and ConditionType.STARS to make asking after sun and sunny items easier
        * [ ] rework answers to (optionally) use a generalized answer that has a slot for the condition
* [ ] **(maybe) add a dict full of aliases for weather conditions to language files and import everything in it as rhasspy slot program as well as map those aliases to conditions (similar to named_days and named_times aliases)**
* [X] **(maybe) export named_days, named_times and their aliases as slot program**
* [X] **rewrite the logic for a detailed weather report (and remove the last hardcoded language stuff with that)**
* [ ] **add in logic for ConditionType.WIND**
    * [ ] add wind as an extra WeatherCondition
        * [X] figure out a wind speed to severity conversion
        * [X] figure out how to write a custom description for wind (owm does not do that for me) and translate that
        * [ ] add filter functionality to only add certain conditions to answers (I do not want to hear about a mild wind in my daily weather report)
    * [ ] define and use items that are useful for wind
    * [ ] make it possible to ask about wind condition
* [ ] **add output system to define how this script outputs**
    * [X] rhasspy hass.io json (current way)
    * [x] extended json (add in an output part to json containing the answer to the question as well as some information) (can be done with the new template system)
    * [X] mqtt
    * [ ] rhasspy_hermes-app
    * [ ] rhasspy web api tts
* [ ] **add parsers for more than rhasspy local command script**
    * [ ] rhasspy_hermes-app
    * [ ] cli (integrate [ulnos cli parser](https://github.com/ulno/cli_weather))
* [ ] **clean up code**
    * [ ] remove all comments referencing snips
    * [ ] replace comments documenting functions with pydoc strings
    * [ ] add documentation for everything that has none
    * [X] figure out a way to have the config globally accessible without having to import it inside functions because it is not initialized otherwise
    * [ ] cleaning up imports in general
    * [X] move definition for warm and cold from language files to config file
    * [ ] find every not implemented feature that could be implemented (StatusCode.NOT_IMPLEMENTED_ERROR)
    * [ ] fix asking for sun at night error
* [ ] **clean up on the rhasspy side of things**
     * [ ] clean up sentences for rhasspy and add some
     * [ ] make asking about stars possible
     * [ ] find some way to ask about a clear sky
     * [X] offer an English translation for rhasspy sentences
* [ ] **add to this readme**
    * [X] table of contents
    * [X] file structure graph
    * [ ] rewrite most of the text
        * [ ] add better introduction
        * [X] add better explanation for setup
        * [X] add explanation of config
        * [X] rewrite functionality part (removed it instead)
        * [ ] split setup explanation into 2.4 and 2.5
