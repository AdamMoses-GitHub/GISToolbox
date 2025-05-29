"""
GIS utility functions: coordinate transforms, bbox, city lookup, etc.
"""

from pyproj import Transformer
from shapely.geometry import Point
from resources.cities import CITIES
import math

def latlon_to_utm(lat, lon):
    zone = int((lon + 180) / 6) + 1
    is_north = lat >= 0
    transformer = Transformer.from_crs("epsg:4326", f"epsg:326{zone:02d}" if is_north else f"epsg:327{zone:02d}", always_xy=True)
    easting, northing = transformer.transform(lon, lat)
    return easting, northing, zone, is_north

def utm_to_latlon(easting, northing, zone, is_north):
    transformer = Transformer.from_crs(f"epsg:326{zone:02d}" if is_north else f"epsg:327{zone:02d}", "epsg:4326", always_xy=True)
    lon, lat = transformer.transform(easting, northing)
    return lat, lon

def round_to_nearest(value, nearest):
    return round(value / nearest) * nearest

def get_bbox_from_centroid(easting, northing, width, height):
    half_w = width / 2
    half_h = height / 2
    return {
        'west': easting - half_w,
        'east': easting + half_w,
        'south': northing - half_h,
        'north': northing + half_h
    }

def bbox_size_meters(bbox):
    return bbox['east'] - bbox['west'], bbox['north'] - bbox['south']

def meters_to_miles(m):
    return m * 0.000621371

def get_nearest_city(centroid):
    # centroid: (lat, lon)
    min_dist = float('inf')
    nearest = None
    for city in CITIES:
        dist = math.hypot(city['lat'] - centroid[0], city['lon'] - centroid[1])
        if dist < min_dist:
            min_dist = dist
            nearest = city['name']
    return nearest
