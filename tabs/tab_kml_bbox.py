"""
Tab 1: Create a KML Bounding Box
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QPushButton, QCheckBox, QGroupBox, QFileDialog, QSizePolicy
)
from widgets.info_box import InfoBox
from gis_utils import latlon_to_utm, utm_to_latlon, round_to_nearest, get_bbox_from_centroid
import shapefile

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
        # Add button to produce the bounding box and save KML/SHP
        self.bbox_btn = QPushButton("Create Bounding Box")
        self.bbox_btn.clicked.connect(self.create_bbox_and_select_kml)
        form.addRow(self.bbox_btn)
        # Layout
        self.layout().addLayout(form)
        self.layout().addStretch()  # Add stretch to push InfoBox to the bottom

        self.info_box = InfoBox()
        self.info_box.setMinimumHeight(140)  # Adjust as needed to match other tabs
        self.info_box.setMaximumHeight(200)  # Optional: limit max height for consistency
        # Fix: Use QSizePolicy.Fixed instead of self.info_box.sizePolicy().Fixed
        self.info_box.setSizePolicy(self.info_box.sizePolicy().horizontalPolicy(), QSizePolicy.Fixed)
        self.layout().addWidget(self.info_box)
        # Set default to Washington Monument
        self.lat.setValue(38.8895)
        self.lon.setValue(-77.0353)
        utm_e, utm_n, utm_z, utm_ns = latlon_to_utm(38.8895, -77.0353)
        self.utm_easting.setValue(utm_e)
        self.utm_northing.setValue(utm_n)
        self.utm_zone.setValue(utm_z)
        self.utm_ns.setCurrentIndex(0 if utm_ns else 1)
        # Connect signals for real-time update
        self.coord_type_combo.currentIndexChanged.connect(self.update_info_box)
        self.lat.valueChanged.connect(self.update_info_box)
        self.lon.valueChanged.connect(self.update_info_box)
        self.utm_easting.valueChanged.connect(self.update_info_box)
        self.utm_northing.valueChanged.connect(self.update_info_box)
        self.utm_zone.valueChanged.connect(self.update_info_box)
        self.utm_ns.currentIndexChanged.connect(self.update_info_box)
        self.width.valueChanged.connect(self.update_info_box)
        self.height.valueChanged.connect(self.update_info_box)
        self.round_utm.valueChanged.connect(self.update_info_box)
        self.toggle_coord_inputs()
        self.update_info_box()

    def toggle_coord_inputs(self):
        utm_enabled = self.coord_type_combo.currentIndex() == 0
        # Only enable UTM widgets if UTM is selected
        for w in [self.utm_easting, self.utm_northing, self.utm_zone, self.utm_ns]:
            w.setEnabled(utm_enabled)
        # Only enable Lat/Lon widgets if Lat/Long is selected
        for w in [self.lat, self.lon]:
            w.setEnabled(not utm_enabled)

    def create_bbox_and_select_kml(self):
        # Update info box first
        self.update_info_box()
        # Prompt user to select KML file to save
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save KML Bounding Box",
            "",
            "KML Files (*.kml);;All Files (*)"
        )
        if file_path:
            self.generate_kml(file_path)
            if self.save_shp.isChecked():
                self.generate_shp(file_path)

    def update_info_box(self):
        # Get centroid in UTM
        if self.coord_type_combo.currentIndex() == 0:
            easting = self.utm_easting.value()
            northing = self.utm_northing.value()
            zone = self.utm_zone.value()
            is_north = self.utm_ns.currentIndex() == 0
        else:
            lat = self.lat.value()
            lon = self.lon.value()
            easting, northing, zone, is_north = latlon_to_utm(lat, lon)

        # Round UTM centroid
        easting = round_to_nearest(easting, self.round_utm.value())
        northing = round_to_nearest(northing, self.round_utm.value())

        # Calculate BBox based on rounded UTM centroid and specified width/height
        bbox = get_bbox_from_centroid(easting, northing, self.width.value(), self.height.value())

        # Prepare corners: [top-left, top-right, bottom-right, bottom-left] in UTM
        utm_corners = [
            (bbox['west'], bbox['north'], zone, is_north),   # top-left
            (bbox['east'], bbox['north'], zone, is_north),   # top-right
            (bbox['east'], bbox['south'], zone, is_north),   # bottom-right
            (bbox['west'], bbox['south'], zone, is_north),   # bottom-left
        ]

        # The info_box will calculate lat/lon corners, min/max extents, and sizes internally.
        # For KML/SHP creation, always WGS84
        self.info_box.update_info(utm_corners, input_crs='utm', native_crs="UTM (user input or derived from Lat/Lon)")

    def generate_kml(self, file_path):
        # This method would use the current state of inputs to generate KML
        # For demonstration, just writes a placeholder KML with the bounding box as a polygon
        utm_corners = self.get_current_utm_corners()
        # Convert UTM corners to lat/lon for KML
        latlon_corners = [utm_to_latlon(e, n, z, ns) for (e, n, z, ns) in utm_corners]
        # KML polygon coordinates string (lon,lat,0)
        coords_str = " ".join([f"{lon},{lat},0" for (lat, lon) in latlon_corners] + [f"{latlon_corners[0][1]},{latlon_corners[0][0]},0"])
        kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <Placemark>
    <name>{self.name_edit.text()}</name>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <coordinates>
            {coords_str}
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
</Document>
</kml>
"""
        with open(file_path, "w") as f:
            f.write(kml)

    def generate_shp(self, file_path):
        # Create a polygon shapefile for the bounding box
        shp_path = file_path.rsplit(".", 1)[0] + ".shp"
        utm_corners = self.get_current_utm_corners()
        # Convert UTM corners to lat/lon for SHP (WGS84)
        latlon_corners = [utm_to_latlon(e, n, z, ns) for (e, n, z, ns) in utm_corners]
        # SHP expects (lon, lat)
        poly_points = [(lon, lat) for (lat, lon) in latlon_corners]
        # Ensure closed polygon
        if poly_points[0] != poly_points[-1]:
            poly_points.append(poly_points[0])
        # Write shapefile
        with shapefile.Writer(shp_path, shapeType=shapefile.POLYGON) as w:
            w.field('NAME', 'C')
            w.poly([poly_points])
            w.record(self.name_edit.text())
        # Write .prj file for WGS84
        prj_path = shp_path.rsplit(".", 1)[0] + ".prj"
        with open(prj_path, "w") as prj:
            prj.write('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]')

    def get_current_utm_corners(self):
        # Helper to get the current UTM corners for export
        if self.coord_type_combo.currentIndex() == 0:
            easting = self.utm_easting.value()
            northing = self.utm_northing.value()
            zone = self.utm_zone.value()
            is_north = self.utm_ns.currentIndex() == 0
        else:
            lat = self.lat.value()
            lon = self.lon.value()
            easting, northing, zone, is_north = latlon_to_utm(lat, lon)
        easting = round_to_nearest(easting, self.round_utm.value())
        northing = round_to_nearest(northing, self.round_utm.value())
        bbox = get_bbox_from_centroid(easting, northing, self.width.value(), self.height.value())
        utm_corners = [
            (bbox['west'], bbox['north'], zone, is_north),   # top-left
            (bbox['east'], bbox['north'], zone, is_north),   # top-right
            (bbox['east'], bbox['south'], zone, is_north),   # bottom-right
            (bbox['west'], bbox['south'], zone, is_north),   # bottom-left
        ]
        return utm_corners
