"""
Reusable InfoBox widget for displaying bounding box and city info.
"""
from PySide6.QtWidgets import QGroupBox, QFormLayout, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from resources.cities import get_nearest_city
from gis_utils import latlon_to_utm, utm_to_latlon

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
        self.form.addRow("Sanity Check, Nearest Major City:", self.city_label)
        self.form.addRow("Current UTM Bounding Box:", self.utm_label)
        self.form.addRow("Current Lat/Long Bounding Box:", self.latlon_label)
        self.form.addRow("Width/Height (meters):", self.size_m_label)
        self.form.addRow("Width/Height (miles):", self.size_mi_label)
        for label in [self.city_label, self.utm_label, self.latlon_label, self.size_m_label, self.size_mi_label]:
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Not editable, but selectable
    def update_info(self, centroid, utm_bbox=None, latlon_bbox=None, size_m=None, size_mi=None, input_crs='wgs84'):
        """
        centroid: tuple (lat, lon) if input_crs='wgs84', or (easting, northing, zone, is_north) if input_crs='utm'
        input_crs: 'wgs84' or 'utm'
        """
        # Convert centroid to both systems
        if input_crs == 'utm':
            easting, northing, zone, is_north = centroid
            lat, lon = utm_to_latlon(easting, northing, zone, is_north)
            utm_str = f"Easting: {easting:.2f}, Northing: {northing:.2f}, Zone: {zone}{'N' if is_north else 'S'}"
            latlon_str = f"Lat: {lat:.6f}, Lon: {lon:.6f}"
        else:
            lat, lon = centroid
            easting, northing, zone, is_north = latlon_to_utm(lat, lon)
            utm_str = f"Easting: {easting:.2f}, Northing: {northing:.2f}, Zone: {zone}{'N' if is_north else 'S'}"
            latlon_str = f"Lat: {lat:.6f}, Lon: {lon:.6f}"
        city = get_nearest_city((lat, lon))
        self.city_label.setText(city)
        self.utm_label.setText(utm_str if utm_bbox is None else utm_bbox)
        self.latlon_label.setText(latlon_str if latlon_bbox is None else latlon_bbox)
        self.size_m_label.setText(size_m if size_m is not None else "-")
        self.size_mi_label.setText(size_mi if size_mi is not None else "-")
