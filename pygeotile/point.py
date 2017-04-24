import math
from .meta import Meta


class Point(Meta):
    def __init__(self, latitude=0.0, longitude=0.0):
        super().__init__()
        self._latitude = latitude
        self._longitude = longitude

    @classmethod
    def from_latitude_longitude(cls, latitude=0.0, longitude=0.0):
        """Creates a point from lat/lon in WGS84"""
        point = cls()
        point.latitude_longitude = latitude, longitude
        return point

    @classmethod
    def from_pixel(cls, pixel_x=0, pixel_y=0, zoom=None):
        """Creates a point from pixels X Y Z (zoom) in pyramid"""
        point = cls()
        meter_x = pixel_x * point.resolution(zoom) - point.origin_shift
        meter_y = pixel_y * point.resolution(zoom) - point.origin_shift
        meter_x, meter_y = point._sign_meters(meters=(meter_x, meter_y), pixels=(pixel_x, pixel_y), zoom=zoom)
        return point.from_meters(meter_x=meter_x, meter_y=meter_y)

    @classmethod
    def from_meters(cls, meter_x=0.0, meter_y=0.0):
        """Creates a point from X Y Z (zoom) meters in Spherical Mercator EPSG:900913"""
        point = cls()
        longitude = (meter_x / point.origin_shift) * 180.0
        latitude = (meter_y / point.origin_shift) * 180.0
        latitude = 180.0 / math.pi * (2 * math.atan(math.exp(latitude * math.pi / 180.0)) - math.pi / 2.0)
        return point.from_latitude_longitude(latitude=latitude, longitude=longitude)

    @property
    def latitude_longitude(self):
        """Gets lat/lon in WGS84"""
        return self._latitude, self._longitude

    @latitude_longitude.setter
    def latitude_longitude(self, value=None):
        """Sets lat/lon in WGS84"""
        if type(value) is tuple:
            latitude, longitude = value
            self._latitude = latitude
            self._longitude = longitude
        else:
            raise TypeError('Arguments of coordinates needs to a tuple of Latitude and Longitude!')

    def pixels(self, zoom=None):
        """Gets pixels of the EPSG:4326 pyramid by a specific zoom, converted from lat/lon in WGS84"""
        meter_x, meter_y = self.meters
        pixel_x = (meter_x + self.origin_shift) / self.resolution(zoom=zoom)
        pixel_y = (meter_y - self.origin_shift) / self.resolution(zoom=zoom)
        return abs(round(pixel_x)), abs(round(pixel_y))

    @property
    def meters(self):
        """Gets the XY meters in Spherical Mercator EPSG:900913, converted from lat/lon in WGS84"""
        latitude, longitude = self.latitude_longitude
        meter_x = longitude * self.origin_shift / 180.0
        meter_y = math.log(math.tan((90.0 + latitude) * math.pi / 360.0)) / (math.pi / 180.0)
        meter_y = meter_y * self.origin_shift / 180.0
        return meter_x, meter_y

    def _sign_meters(self, meters, pixels, zoom):
        half_size = int((self.tile_size * 2 ** zoom) / 2)
        pixel_x, pixel_y = pixels
        meter_x, meter_y = meters
        meter_x, meter_y = abs(meter_x), abs(meter_y)
        if pixel_x < half_size:
            meter_x *= -1
        if pixel_y > half_size:
            meter_y *= -1
        return meter_x, meter_y
