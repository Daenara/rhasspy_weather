# Datadump for a Location
class Location:
    def __init__(self, city):
        self.city = city

    def set_lat_and_lon(self, lat, lon):
        self.lat = float(lat)
        self.lon = float(lon)

    def set_zipcode(self, zipcode, country_code):
        self.zipcode = zipcode
        self.country_code = country_code