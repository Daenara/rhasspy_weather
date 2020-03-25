import datetime
from rhasspy_weather.weather_helpers import DateType, ForecastType, Location, Grain

##########  Weather Request ##########

# Class holding all the information that parse_intent_message found
# has many functions to return the information in
# human- and machinereadable ways
class WeatherRequest:
    """
    Class holding all the information that parse_intent_message found
    has many functions to return the information in 
    human- and machinereadable ways
    Attributes:
    date_type : DateType
        Is the request for a fixed time or an interval
    grain : Grain
        How specific should the request be, days, hours
    request_date : datetime.date
        For when is the request
    location : str
        For where is the request
    requested : str
        Was a specific condition, item or temperature requested
    time_specified : str
        non parsed time for the request (used for output)
    forecast_type : ForecastType
        Type of request, full, temperature, condition or item
    detail : bool
        True for detailed answer, else use False
    start_time : datetime.time
    end_time : datetime.time
    weekday : str
    string_date :str
    readable_date : str
    string_start_time : str
    readable_start_time : str
    string_end_time : str
    readable_end_time : str
    time_difference : int
        number of days between today and the requested date
    """

    def __init__(self, date_type, grain, request_date, forecast_type, detail):
        """
        Parameters:
        date_type : DateType
        grain : Grain
        request_date : datetime.date
        forecast_type : ForecastType
        detail : bool
        """
        self.date_type = date_type
        self.grain = grain
        self.request_date = request_date
        self.location = ""
        self.requested = ""
        self.time_specified = ""
        self.date_specified = ""
        self.forecast_type = forecast_type
        self.detail = detail
    
    def __str__(self): 
        return "(" + str(self.forecast_type) + ", " + str(self.date_type) + ", " + \
               str(self.grain) + ", " + self.string_date + ", " + str(self.start_time) + \
               ", " + str(self.end_time) + ", " + self.location + ", " + self.requested + ")"
    
    def __get_valid_time(self, val):
        if type(val) is datetime.time:
            time = val
        elif type(val) is str:
            try:
                time = datetime.datetime.strptime(val, "%H:%M:%S").time()
            except ValueError:
                hours, minutes, seconds = map(int, "00:00:00".split(':'))
                if hours >= 24 and 0 <= minutes < 60 and 0 <= seconds < 60: 
                    time = datetime.time(0,minutes,seconds)
        if time:
            # if the weather at midnight was requested change the day to the
            # next day
            # (snips thinks midnight means 00:00AM of the day requested, I say
            # it is after 11:59PM of the day requested)
            if self.grain == Grain.HOUR and time == datetime.time.min:
                self.request_date = self.request_date + datetime.timedelta(days=1)
            elif self.grain == Grain.HOUR and self.request_date == datetime.datetime.now().date() and \
                datetime.datetime.now().time() > time and time < datetime.time(12,0):
               return time.replace(hour=time.hour + 12)
            return time
        return -1 # somehing was wrong with the time
    
    @property
    def grain(self):
        return self.__grain
    @grain.setter
    def grain(self, val):
        if type(val) is Grain:
            self.__grain = val
    
    @property
    def date_type(self):
        return self.__date_type
    @date_type.setter
    def date_type(self, val):
        if type(val) is DateType:
            self.__date_type = val
    
    @property
    def forecast_type(self):
        return self.__forecast_type
    @forecast_type.setter
    def forecast_type(self, val):
        if type(val) is ForecastType:
            self.__forecast_type = val
    
    @property
    def request_date(self):
        return self.__request_date
    @request_date.setter
    def request_date(self, val):
        if type(val) is datetime.date:
            self.__request_date = val
        elif type(val) is str:
            self.__request_date = datetime.datetime.strptime(val, "%Y-%m-%d").date()
        else:
            self.__request_date = -1
    
    @property
    def start_time(self):
        if '_WeatherRequest__start_time' in self.__dict__:
            return self.__start_time
        return None
    @start_time.setter
    def start_time(self, val):
        self.__start_time = self.__get_valid_time(val)
        
    @property
    def end_time(self):
        if '_WeatherRequest__end_time' in self.__dict__:
            return self.__end_time
        return None
    @end_time.setter
    def end_time(self, val):
        self.__end_time = self.__get_valid_time(val)
    
    @property
    def weekday(self):
        return self.request_date.strftime("%A")
        
    @property
    def readable_date(self):
        return self.request_date.strftime("%d. %B")
        
    @property
    def string_date(self):
        return self.request_date.strftime("%Y-%m-%d")
        
    @property
    def string_start_time(self):
        return self.start_time.strftime("%H:%M:%S")
        
    @property
    def string_end_time(self):
        return self.end_time.strftime("%H:%M:%S")
    
    @property
    def readable_start_time(self):
        return self.start_time.strftime("%H:%M")
        
    @property
    def readable_end_time(self):
        return self.end_time.strftime("%H:%M")
        
    @property
    def time_difference(self):
        time_difference = (self.request_date - datetime.date.today()).days
        if self.grain == Grain.HOUR and self.start_time == datetime.time(0,0,0):
            return (time_difference - 1)
        return time_difference