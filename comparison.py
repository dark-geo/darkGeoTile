from pygeotile.tile import Tile as pgtTile
import darkgeotile
import timeit
import random


dgtTile = darkgeotile.get_Tile('+init=epsg:3857')

num = 10**5

for_meters_args_list = [(
    random.random() * dgtTile.x_len + dgtTile.min_x,
    random.random() * dgtTile.y_len + dgtTile.min_y,
    random.randint(0, 18)
) for _ in range(10)]


def for_meters_measure_func(TileClass):
    for args in for_meters_args_list:
        TileClass.for_meters(*args)


pgt_time = timeit.timeit('for_meters_measure_func(pgtTile)', number=num, globals=globals())
dgt_time = timeit.timeit('for_meters_measure_func(dgtTile)', number=num, globals=globals())

print(
    f'pyGeoTile method `for_meters`: {pgt_time}',
    f'darkGeoTile method `for_meters`: {dgt_time}',
    sep='\n'
)

for_latitude_longitude_args_list = [(
    random.random() * 180. - 90.,
    random.random() * 360. - 180.,
    random.randint(0, 18)
) for _ in range(10)]


def for_latitude_longitude_measure_func(TileClass):
    for args in for_latitude_longitude_args_list:
        TileClass.for_latitude_longitude(*args)


pgt_time = timeit.timeit('for_latitude_longitude_measure_func(pgtTile)', number=num, globals=globals())
dgt_time = timeit.timeit('for_latitude_longitude_measure_func(dgtTile)', number=num, globals=globals())

print(
    f'pyGeoTile method `for_latitude_longitude`: {pgt_time}',
    f'darkGeoTile method `for_latitude_longitude`: {dgt_time}',
    sep='\n'
)