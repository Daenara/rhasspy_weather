# rhasspy Weather

A python script that can make rhasspy voice assistant tell the weather.

## Found a bug?
Just open an issue and supply me with the sentence that produced the bug. 

## Table of Contents
* [Setup (out of date, will be fixed soon)](#setup)
* [Usage](#usage)
* [Development](#development)
    * [Project Structure](#project-structure)
* [TODO](#todo)

## Setup
For setup instructions see the project wiki.

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
(needs updating, refer to github)
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

## TODO
(needs updating also, I might have done more than I remember doing)
* [X] **Rework the item system for requests**
    * [X] add custom item class saving name, grammar information and condition type
        * [X] properly format item for output
        * [X] output conditions it can be useful in
    * [X] write wrapper class to hold those items
        * [X] find if item is in list
        * [X] (maybe) list items by condition
        * [X] export items to rhasspy slot program
    * [X] while at it, add in new item types (there are types in my rhasspy slot the logic does not now and parts in the logic that rhasspy does not know)
    * [X] actually use the new item system
        * [X] replace function from language files
        * [X] add in new condition types
        * [X] actually use ConditionType for conditions
        * [X] add ConditionType.SUN and ConditionType.STARS to make asking after sun and sunny items easier
        * [ ] rework answers to (optionally) use a generalized answer that has a slot for the condition
* [X] **(maybe) add a dict full of aliases for weather conditions to language files and import everything in it as rhasspy slot program as well as map those aliases to conditions (similar to named_days and named_times aliases)**
* [X] **(maybe) export named_days, named_times and their aliases as slot program**
* [X] **rewrite the logic for a detailed weather report (and remove the last hardcoded language stuff with that)**
* [X] **add in logic for ConditionType.WIND**
    * [X] add wind as an extra WeatherCondition
        * [X] figure out a wind speed to severity conversion
        * [X] figure out how to write a custom description for wind (owm does not do that for me) and translate that
        * [ ] add filter functionality to only add certain conditions to answers (I do not want to hear about a mild wind in my daily weather report)
    * [X] define and use items that are useful for wind
    * [X] make it possible to ask about wind condition
* [X] **add output system to define how this script outputs**
    * [X] rhasspy hass.io json (current way)
    * [x] extended json (add in an output part to json containing the answer to the question as well as some information) (can be done with the new template system)
    * [X] mqtt
    * [X] rhasspy_hermes-app (called return)
    * [X] rhasspy web api tts
* [X] **add parsers for more than rhasspy local command script**
    * [X] rhasspy_hermes-app (called nlu_intent)
    * [X] cli (integrate [ulnos cli parser](https://github.com/ulno/cli_weather))
* [ ] **clean up code**
    * [X] remove all comments referencing snips
    * [ ] replace comments documenting functions with pydoc strings
    * [ ] add documentation for everything that has none
    * [X] figure out a way to have the config globally accessible without having to import it inside functions because it is not initialized otherwise
    * [ ] cleaning up imports in general
    * [X] move definition for warm and cold from language files to config file
    * [ ] find every not implemented feature that could be implemented (StatusCode.NOT_IMPLEMENTED_ERROR)
    * [X] fix asking for sun at night error
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
