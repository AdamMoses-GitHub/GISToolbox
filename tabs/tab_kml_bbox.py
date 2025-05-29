"""
Tab 1: Create a KML Bounding Box
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton, QCheckBox, QGroupBox, QRadioButton)
from widgets.info_box import InfoBox
from gis_utils import latlon_to_utm, utm_to_latlon, round_to_nearest, get_bbox_from_centroid, bbox_size_meters, meters_to_miles

class KMLBoundingBoxTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        form = QFormLayout()
        # Name
        self.name_edit = QLineEdit()
        form.addRow("KML Object Name:", self.name_edit)
        # Coordinate input type
        self.coord_type_combo = QComboBox()
        self.coord_type_combo.addItems(["UTM", "Lat/Long"])
        self.coord_type_combo.currentIndexChanged.connect(self.toggle_coord_inputs)
        form.addRow("Input Coordinate Type:", self.coord_type_combo)
        # UTM inputs
        utm_box = QGroupBox("UTM Centroid Input")
        utm_layout = QHBoxLayout()
        self.utm_easting = QDoubleSpinBox()
        self.utm_easting.setRange(100000, 900000)
        self.utm_easting.setDecimals(2)
        self.utm_northing = QDoubleSpinBox()
        self.utm_northing.setRange(0, 10000000)
        self.utm_northing.setDecimals(2)
        self.utm_zone = QSpinBox()
        self.utm_zone.setRange(1, 60)
        self.utm_ns = QComboBox()
        self.utm_ns.addItems(["North", "South"])
        utm_layout.addWidget(QLabel("Easting:"))
        utm_layout.addWidget(self.utm_easting)
        utm_layout.addWidget(QLabel("Northing:"))
        utm_layout.addWidget(self.utm_northing)
        utm_layout.addWidget(QLabel("Zone:"))
        utm_layout.addWidget(self.utm_zone)
        utm_layout.addWidget(self.utm_ns)
        utm_box.setLayout(utm_layout)
        form.addRow(utm_box)
        # Lat/Long inputs
        latlon_box = QGroupBox("Lat/Long Centroid Input")
        latlon_layout = QHBoxLayout()
        self.lat = QDoubleSpinBox()
        self.lat.setRange(-90, 90)
        self.lat.setDecimals(6)
        self.lon = QDoubleSpinBox()
        self.lon.setRange(-180, 180)
        self.lon.setDecimals(6)
        latlon_layout.addWidget(QLabel("Latitude:"))
        latlon_layout.addWidget(self.lat)
        latlon_layout.addWidget(QLabel("Longitude:"))
        latlon_layout.addWidget(self.lon)
        latlon_box.setLayout(latlon_layout)
        form.addRow(latlon_box)
        # Rounding
        self.round_utm = QSpinBox()
        self.round_utm.setRange(1, 1000)
        self.round_utm.setValue(10)
        form.addRow("Round Centroid to Nearest UTM Meter:", self.round_utm)
        # Width/Height
        self.width = QSpinBox()
        self.width.setRange(1, 100000)
        self.width.setValue(1000)
        self.height = QSpinBox()
        self.height.setRange(1, 100000)
        self.height.setValue(1000)
        form.addRow("Width (meters):", self.width)
        form.addRow("Height (meters):", self.height)
        # SHP toggle
        self.save_shp = QCheckBox("Save Shapefile (SHP) alongside KML")
        form.addRow(self.save_shp)
        # Layout
        self.layout().addLayout(form)
        self.info_box = InfoBox()
        self.layout().addWidget(self.info_box)
        # Set default to Washington Monument
        self.lat.setValue(38.8895)
        self.lon.setValue(-77.0353)
        utm_e, utm_n, utm_z, utm_ns = latlon_to_utm(38.8895, -77.0353)
        self.utm_easting.setValue(utm_e)
        self.utm_northing.setValue(utm_n)
        self.utm_zone.setValue(utm_z)
        self.utm_ns.setCurrentIndex(0 if utm_ns else 1)
        # Connect signals
        self.coord_type_combo.setCurrentIndex(1)  # Default to Lat/Long
        self.toggle_coord_inputs()
        self.lat.valueChanged.connect(self.update_info_box)
        self.lon.valueChanged.connect(self.update_info_box)
        self.utm_easting.valueChanged.connect(self.update_info_box)
        self.utm_northing.valueChanged.connect(self.update_info_box)
        self.utm_zone.valueChanged.connect(self.update_info_box)
        self.utm_ns.currentIndexChanged.connect(self.update_info_box)
        self.width.valueChanged.connect(self.update_info_box)
        self.height.valueChanged.connect(self.update_info_box)
        self.round_utm.valueChanged.connect(self.update_info_box)
        self.update_info_box()
    def toggle_coord_inputs(self):
        utm_enabled = self.coord_type_combo.currentIndex() == 0
        for w in [self.utm_easting, self.utm_northing, self.utm_zone, self.utm_ns]:
            w.setEnabled(utm_enabled)
        for w in [self.lat, self.lon]:
            w.setEnabled(not utm_enabled)
        self.update_info_box()
    def update_info_box(self):
        # Get centroid in UTM
        if self.coord_type_combo.currentIndex() == 0:
            easting = self.utm_easting.value()
            northing = self.utm_northing.value()
            zone = self.utm_zone.value()
            is_north = self.utm_ns.currentIndex() == 0
            lat, lon = utm_to_latlon(easting, northing, zone, is_north)
        else:
            lat = self.lat.value()
            lon = self.lon.value()
            easting, northing, zone, is_north = latlon_to_utm(lat, lon)
        # Round
        easting = round_to_nearest(easting, self.round_utm.value())
        northing = round_to_nearest(northing, self.round_utm.value())
        # BBox
        bbox = get_bbox_from_centroid(easting, northing, self.width.value(), self.height.value())
        width_m, height_m = bbox_size_meters(bbox)
        width_mi = meters_to_miles(width_m)
        height_mi = meters_to_miles(height_m)
        utm_bbox = f"E: {bbox['east']:.2f}, W: {bbox['west']:.2f}, N: {bbox['north']:.2f}, S: {bbox['south']:.2f}"
        latlon_bbox = f"E: {utm_to_latlon(bbox['east'], northing, zone, is_north)[1]:.6f}, W: {utm_to_latlon(bbox['west'], northing, zone, is_north)[1]:.6f}, N: {utm_to_latlon(easting, bbox['north'], zone, is_north)[0]:.6f}, S: {utm_to_latlon(easting, bbox['south'], zone, is_north)[0]:.6f}"
        size_m = f"{width_m:.2f} x {height_m:.2f}"
        size_mi = f"{width_mi:.2f} x {height_mi:.2f}"
        self.info_box.update_info((lat, lon), utm_bbox, latlon_bbox, size_m, size_mi)
