class Location:
    def __init__(self, city, zipcode=None, country_code=None, lat=None, lon=None):
        self.city = city
        self.name = city  # used for output only, intended for custom queries like how is the weather at grandmas (not implemented yet)
        if not ((lat is None or lon is None) or (lat == "" or lon == "")):
            self.lat = lat
            self.lon = lon
        if not (zipcode is None or country_code is None) or (zipcode is "" or country_code is ""):
            self.zipcode = zipcode
            self.country_code = country_code

    def set_lat_and_lon(self, lat, lon):
        self.lat = float(lat)
        self.lon = float(lon)

    def set_zipcode(self, zipcode, country_code):
        self.zipcode = zipcode
        self.country_code = country_code
