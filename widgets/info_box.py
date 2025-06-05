"""
Reusable InfoBox widget for displaying bounding box and city info.
"""
from PySide6.QtWidgets import QGroupBox, QFormLayout, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from resources.cities import get_nearest_city
from gis_utils import latlon_to_utm, utm_to_latlon
import math

class InfoBox(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Bounding Box Info")
        self.setLayout(QVBoxLayout())
        self.form = QFormLayout()
        self.layout().addLayout(self.form)
        self.city_label = QLabel()
        self.utm_label = QLabel()
        self.latlon_label = QLabel()
        self.size_m_label = QLabel()
        self.size_mi_label = QLabel()
        self.crs_label = QLabel()  # Add CRS label
        self.form.addRow("Sanity Check, Nearest Major City:", self.city_label)
        self.form.addRow("UTM Extents (min/max):", self.utm_label)
        self.form.addRow("Lat/Lon Extents (min/max):", self.latlon_label)
        self.form.addRow("Width/Height (meters):", self.size_m_label)
        self.form.addRow("Width/Height (miles):", self.size_mi_label)
        self.form.addRow("Native CRS:", self.crs_label)  # Add CRS row
        for label in [self.city_label, self.utm_label, self.latlon_label, self.size_m_label, self.size_mi_label, self.crs_label]:
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Not editable, but selectable

    def update_info(self, bbox, utm_bbox=None, latlon_bbox=None, size_m=None, size_mi=None, input_crs='wgs84', native_crs=None):
        """
        bbox: list of 4 tuples (corners) in input_crs order: [top-left, top-right, bottom-right, bottom-left]
              For 'wgs84', tuples should be (lon, lat).
              For 'utm', tuples should be (easting, northing, zone, is_north).
        input_crs: 'wgs84' or 'utm'
        """
        # Always convert corners to both UTM and lat/lon for consistent display
        if input_crs == 'utm':
            utm_corners = bbox
            # Convert UTM corners to Lat/Lon
            latlon_corners = [utm_to_latlon(e, n, z, ns) for (e, n, z, ns) in bbox]
        else: # Assuming input_crs is 'wgs84' or similar geographic, expecting (lon, lat)
            latlon_corners = bbox
            # Convert Lat/Lon corners to UTM
            utm_corners = [latlon_to_utm(lat, lon) for (lon, lat) in bbox] # Note: latlon_to_utm expects (lat, lon)

        # UTM extents
        if utm_corners:
            easting_vals = [e for (e, n, z, ns) in utm_corners]
            northing_vals = [n for (e, n, z, ns) in utm_corners]
            min_e, max_e = min(easting_vals), max(easting_vals)
            min_n, max_n = min(northing_vals), max(northing_vals)
            # Assuming all UTM corners are in the same zone/hemisphere
            utm_zone = utm_corners[0][2] if utm_corners[0][2] is not None else 'N/A'
            utm_ns = 'N' if (utm_corners[0][3] if utm_corners[0][3] is not None else True) else 'S' # Default to North if unknown

            utm_str = (
                f"Easting: {min_e:.2f} to {max_e:.2f}, "
                f"Northing: {min_n:.2f} to {max_n:.2f}, "
                f"Zone: {utm_zone}{utm_ns if utm_zone != 'N/A' else ''}"
            )

            # Calculate width/height in meters (UTM)
            # Width: distance between top-left and top-right UTM corners
            # Height: distance between top-left and bottom-left UTM corners
            def utm_distance(p1, p2):
                 # p1 and p2 are (easting, northing, zone, is_north) tuples
                 # Ensure they are in the same zone/hemisphere for meaningful distance
                 if p1[2] != p2[2] or p1[3] != p2[3]:
                     # Cannot calculate meaningful distance across zones/hemispheres directly
                     return 0
                 return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

            # Find corners in utm_corners list corresponding to top-left, top-right, bottom-left
            # This assumes the input bbox list order is [top-left, top-right, bottom-right, bottom-left]
            if len(utm_corners) == 4:
                width_m = utm_distance(utm_corners[0], utm_corners[1])
                height_m = utm_distance(utm_corners[0], utm_corners[3])
            else:
                width_m = 0
                height_m = 0

            width_mi = width_m / 1609.344
            height_mi = height_m / 1609.344

            self.size_m_label.setText(f"{width_m:.2f} x {height_m:.2f}")
            self.size_mi_label.setText(f"{width_mi:.2f} x {height_mi:.2f}")
        else:
            utm_str = "N/A"
            self.size_m_label.setText("-")
            self.size_mi_label.setText("-")


        # Lat/Lon extents
        if latlon_corners:
            # Assuming latlon_corners are (lat, lon) from utm_to_latlon or (lon, lat) from input bbox
            # Let's explicitly handle (lon, lat) input for wgs84
            if input_crs != 'utm': # Input was likely (lon, lat)
                 lat_vals = [lat for (lon, lat) in latlon_corners]
                 lon_vals = [lon for (lon, lat) in latlon_corners]
            else: # Input was UTM, converted to (lat, lon) by utm_to_latlon
                 lat_vals = [lat for (lat, lon) in latlon_corners]
                 lon_vals = [lon for (lat, lon) in latlon_corners]

            min_lat, max_lat = min(lat_vals), max(lat_vals)
            min_lon, max_lon = min(lon_vals), max(lon_vals)

            latlon_str = (
                f"Lat: {min_lat:.6f} to {max_lat:.6f}, "
                f"Lon: {min_lon:.6f} to {max_lon:.6f}"
            )

            # Calculate centroid for city lookup (in lat/lon)
            centroid_lat = sum(lat_vals) / len(lat_vals) if lat_vals else 0
            centroid_lon = sum(lon_vals) / len(lon_vals) if lon_vals else 0
            city, city_lat, city_lon = get_nearest_city((centroid_lat, centroid_lon), return_coords=True)

            # Calculate distance to nearest city (Haversine formula)
            def haversine(lat1, lon1, lat2, lon2):
                from math import radians, sin, cos, sqrt, atan2
                R = 6371.0  # Earth radius in kilometers
                dlat = radians(lat2 - lat1)
                dlon = radians(lon2 - lon1)
                a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                return R * c

            dist_km = haversine(centroid_lat, centroid_lon, city_lat, city_lon)
            dist_mi = dist_km * 0.621371

            self.city_label.setText(f"{city} ({dist_km:.1f} km / {dist_mi:.1f} mi)")
        else:
            latlon_str = "N/A"
            self.city_label.setText("N/A")


        self.utm_label.setText(utm_str if utm_bbox is None else utm_bbox)
        self.latlon_label.setText(latlon_str if latlon_bbox is None else latlon_bbox)

        # Set CRS label
        if native_crs:
            self.crs_label.setText(str(native_crs))
        else:
            # Show a default or inferred CRS
            if input_crs == 'utm':
                self.crs_label.setText("UTM")
            elif input_crs == 'wgs84':
                self.crs_label.setText("WGS84")
            else:
                self.crs_label.setText("Unknown")
