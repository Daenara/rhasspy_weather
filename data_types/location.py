class Location:
    def __init__(self, city):
        self.city = city
        self.name = city  # used for output only, intended for custom queries like how is the weather at grandmas (not implemented yet)

    def set_lat_and_lon(self, lat, lon):
        self.lat = float(lat)
        self.lon = float(lon)

    def set_zipcode(self, zipcode, country_code):
        self.zipcode = zipcode
        self.country_code = country_code
