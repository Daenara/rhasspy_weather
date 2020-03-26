# Datadump for a WeatherCondition
class WeatherCondition:
    def __init__(self, severity, description, condition):
        self.severity = severity
        self.description = description
        self.condition = condition

    def __eq__(self, other):
        return self.description == other.description