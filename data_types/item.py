class WeatherItem:

    def __init__(self, name, prefix, suffix, condition_type_list):
        self.__name = name
        self.__prefix = prefix
        self.__suffix = suffix
        self.__condition_list = condition_type_list

    @property
    def name(self):
        return self.__name

    @property
    def conditions(self):
        return self.__condition_list

    def is_for_condition_type(self, condition_type):
        return condition_type in self.__condition_list

    def format_for_output(self):
        output = self.__name
        if self.__prefix != "":
            output = self.__prefix + " " + output
        if self.__suffix != "":
            output = output + " " + self.__suffix
        return output
