import math
import re
from functools import reduce
from typing import Tuple

import pyproj


class BaseTile:
    # Attributes for overwriting:
    projection: pyproj.Proj
    proj_bounds: Tuple[float, float, float, float]
    tile_size: int

    # Attributes created in Tile.__init_subclass__:
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    x_len: float
    y_len: float

    def __init_subclass__(cls, **kwargs):
        assert hasattr(cls, 'projection')
        assert hasattr(cls, 'proj_bounds')
        assert hasattr(cls, 'tile_size')

        cls.min_x, cls.min_y, cls.max_x, cls.max_y = cls.proj_bounds
        cls.x_len = cls.max_x - cls.min_x
        cls.y_len = cls.max_y - cls.min_y

        return super().__init_subclass__(**kwargs)

    def __init__(self, *, tms_x, tms_y, zoom):
        self.tms_x = tms_x
        self.tms_y = tms_y
        self.zoom = zoom

    def __repr__(self):
        return f'Tile(tms_x={self.tms_x}, tms_y={self.tms_y}, zoom={self.zoom})'

    @classmethod
    def from_tms(cls, tms_x, tms_y, zoom):
        """Creates a tile from Tile Map Service (TMS) X Y and zoom"""
        max_tile = (2**zoom) - 1
        assert 0 <= tms_x <= max_tile, 'TMS X needs to be a value between 0 and (2^zoom) -1.'
        assert 0 <= tms_y <= max_tile, 'TMS Y needs to be a value between 0 and (2^zoom) -1.'
        return cls(tms_x=tms_x, tms_y=tms_y, zoom=zoom)

    @classmethod
    def from_google(cls, google_x, google_y, zoom):
        """Creates a tile from Google format X Y and zoom"""
        max_tile = (2**zoom) - 1
        assert 0 <= google_x <= max_tile, 'Google X needs to be a value between 0 and (2^zoom) -1.'
        assert 0 <= google_y <= max_tile, 'Google Y needs to be a value between 0 and (2^zoom) -1.'
        return cls(tms_x=google_x, tms_y=max_tile - google_y, zoom=zoom)

    @classmethod
    def from_quad_tree(cls, quad_tree):
        """Creates a tile from a Microsoft QuadTree"""
        assert bool(
            re.match('^[0-3]*$', quad_tree)), 'QuadTree value can only consists of the digits 0, 1, 2 and 3.'
        zoom = len(str(quad_tree))
        offset = int(math.pow(2, zoom)) - 1
        google_x, google_y = [reduce(lambda result, bit: (result << 1) | bit, bits, 0)
                              for bits in zip(*(reversed(divmod(digit, 2))
                                                for digit in (int(c) for c in str(quad_tree))))]
        return cls(tms_x=google_x, tms_y=(offset - google_y), zoom=zoom)

    @classmethod
    def for_pixels(cls, pixel_x, pixel_y, zoom):
        """Creates a tile from pixels X Y Z (zoom) in pyramid"""
        tms_x = int(math.ceil(pixel_x / float(cls.tile_size)) - 1)
        tms_y = 2**zoom - int(math.ceil(pixel_y / float(cls.tile_size)))
        return cls(tms_x=tms_x, tms_y=tms_y, zoom=zoom)

    @classmethod
    def for_xy(cls, x, y, zoom):
        """Creates a tile from x, y coordinates in given projection"""
        pixels_size = cls.tile_size * 2**zoom

        pixel_x = math.ceil((x - cls.min_x) / cls.x_len * pixels_size)
        pixel_y = pixels_size - math.ceil((y - cls.min_y) / cls.y_len * pixels_size)
        return cls.for_pixels(pixel_x, pixel_y, zoom)

    @classmethod
    def for_meters(cls, meter_x, meter_y, zoom):
        """Creates a tile including point with meters coordinates"""
        if cls.projection.is_latlong():
            raise NotImplementedError('Not for geographic projection')
        return cls.for_xy(meter_x, meter_y, zoom)

    @classmethod
    def for_latitude_longitude(cls, latitude, longitude, zoom):
        """Creates a tile including point with lat/long coordinates"""
        if cls.projection.is_latlong():
            return cls.for_xy(longitude, latitude, zoom)
        return cls.for_xy(*cls.projection(longitude, latitude), zoom)

    @property
    def quad_tree(self):
        """Gets the tile in the Microsoft QuadTree format, converted from TMS"""
        value = ''
        tms_x, tms_y = self.tms
        tms_y = (2**self.zoom - 1) - tms_y
        for i in range(self.zoom, 0, -1):
            digit = 0
            mask = 1 << (i - 1)
            if (tms_x & mask) != 0:
                digit += 1
            if (tms_y & mask) != 0:
                digit += 2
            value += str(digit)
        return value

    @property
    def tms(self):
        """Gets the tile in pyramid from Tile Map Service (TMS)"""
        return self.tms_x, self.tms_y

    @property
    def google(self):
        """Gets the tile in the Google format, converted from TMS"""
        tms_x, tms_y = self.tms
        return tms_x, (2**self.zoom - 1) - tms_y

    @property
    def bounds(self):
        """
        Gets the bounds of a tile represented as the most west and south point and the most east and north point
        !!! Returns tuple of coordinates versus pygeotile.tile.Tile.bounds property
        """
        left_pix, bottom_pix = self.tms_x * self.tile_size, self.tms_y * self.tile_size
        right_pix, top_pix = (self.tms_x + 1) * self.tile_size - 1, (self.tms_y + 1) * self.tile_size - 1

        pixels_size = self.tile_size * 2**self.zoom
        in_one_pixel = (self.x_len / pixels_size, self.y_len / pixels_size)
        return (
            (in_one_pixel[0] * left_pix + self.min_x, in_one_pixel[1] * bottom_pix + self.min_y),
            (in_one_pixel[0] * (right_pix + 1) + self.min_x, in_one_pixel[1] * (top_pix + 1) + self.min_y)
        )


def get_Tile(projection_, proj_bounds_, tile_size_=256):
    class Tile(BaseTile):
        projection = projection_
        proj_bounds = proj_bounds_
        tile_size = tile_size_

    return Tile
