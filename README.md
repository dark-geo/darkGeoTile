# darkGeoTile
Python package for translation between tiles and points coordinate systems. 
Inspired by [geometalab/pyGeoTile](https://github.com/geometalab/pyGeoTile) package, 
darkGeoTile expands functionality for tiles specified in different coordinate systems.

Transformations between cartographic projections systems 
implemented using [jswhit/pyproj](https://github.com/jswhit/pyproj) interface to 
[OSGeo/proj.4](https://github.com/OSGeo/proj.4) project. 

## Usage
The package darkGeoTile consist of function, that returns `pygeotile.tile.Tile`-like class. 
Most methods of this class does the same, but because of removing `Point` class, 
there are some differences (for details look methods docs).

### Example
```python
from darkgeotile import get_tile_class

Tile = get_tile_class('+init=epsg:3857')

tms_x, tms_y, zoom = 134494, 329369, 19
tile = Tile.from_tms(tms_x=tms_x, tms_y=tms_y, zoom=19)  # Tile Map Service (TMS) X Y and zoom

print('QuadTree: ', tile.quad_tree)  # QuadTree:  0302222310303211330
print('Google: ', tile.google)  # Google:  (134494, 194918)
```

Supports Python 3.6, 3.7.
