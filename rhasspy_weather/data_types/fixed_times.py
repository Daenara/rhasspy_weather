import datetime
from enum import Enum


class FixedTimes(Enum):
    MORNING = (datetime.time(0, 0), datetime.time(11, 59))
    AFTERNOON = (datetime.time(12, 0), datetime.time(17, 59))
    EVENING = (datetime.time(18, 0), datetime.time(23, 59))
