from setuptools import setup, find_packages

setup(
    name='darkGeoTile',
    version='1.0.0',
    description='Python package for translation '
                'between tiles and points coordinate systems using different projections',
    url='https://github.com/dark-geo/darkGeoTile',
    license='MIT',
    packages=find_packages(exclude=('comparison.py', ))
)
