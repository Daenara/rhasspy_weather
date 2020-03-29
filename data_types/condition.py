class WeatherCondition:
    def __init__(self, severity, description, condition):
        self.severity = severity
        self.description = description
        self.condition = condition

    def __eq__(self, other):
        return self.description == other.description
        
    def __str__(self):
        return "[" + str(self.condition) + ", " + str(self.severity) + ", " + str(self.description) + "]"
        
    def __repr__(self):
        return "[" + str(self.condition) + ", " + str(self.severity) + ", " + str(self.description) + "]"