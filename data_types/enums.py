from enum import Enum

# WeatherRequest for a fixed time or an interval?
class DateType(Enum):
    FIXED = "fixed"
    INTERVAL = "interval"

# What kind of WeatherRequest was made?
class ForecastType(Enum):
    FULL = "full"
    TEMPERATURE = "temperature"
    ITEM = "item"
    CONDITION = "condition"
    
# my implementation of hermes-pythons Grain since that is the only thing I need from that package
class Grain(Enum):
    YEAR = 0
    QUARTER = 1
    MONTH = 2
    WEEK = 3
    DAY = 4
    HOUR = 5