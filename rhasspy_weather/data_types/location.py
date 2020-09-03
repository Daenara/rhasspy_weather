class Location:
    def __init__(self, city, zipcode=None, country_code=None, lat=None, lon=None):
        self.city = city
        self.name = city  # used for output only, intended for custom queries like how is the weather at grandmas (not implemented yet)
        if lat and lon:
            self.lat = lat
            self.lon = lon
            self.sunrise, self.sunset = self.calculate_sunrise_and_sunset(lat, lon)
        if zipcode and country_code:
            self.zipcode = zipcode
            self.country_code = country_code
        self.sunrise = None
        self.sunset = None

    def set_lat_and_lon(self, lat, lon):
        self.lat = float(lat)
        self.lon = float(lon)
        self.sunrise, self.sunset = self.calculate_sunrise_and_sunset(lat, lon)

    def set_zipcode(self, zipcode, country_code):
        self.zipcode = zipcode
        self.country_code = country_code

    @staticmethod
    def calculate_sunrise_and_sunset(lat, lon):
        import suntime

        sun = suntime.Sun(lat, lon)
        sunrise = sun.get_local_sunrise_time().time()
        sunset = sun.get_local_sunset_time().time()

        return sunrise, sunset
