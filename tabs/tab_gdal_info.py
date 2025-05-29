"""
Tab 2: GDAL Info on a File
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel)
from widgets.info_box import InfoBox
import subprocess
import os

class GDALInfoTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        # File chooser
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected.")
        self.choose_btn = QPushButton("Choose GIS Raster File")
        self.choose_btn.clicked.connect(self.choose_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.choose_btn)
        self.layout().addLayout(file_layout)
        # Process button
        self.process_btn = QPushButton("Process GDAL Info")
        self.process_btn.clicked.connect(self.process_file)
        self.layout().addWidget(self.process_btn)
        # Output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout().addWidget(self.output)
        # Info box
        self.info_box = InfoBox()
        self.layout().addWidget(self.info_box)
        self.selected_file = None
    def choose_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select GIS Raster File", "", "Raster Files (*.tif *.tiff *.img *.vrt *.asc *.bil *.nc);;All Files (*)")
        if file:
            self.selected_file = file
            self.file_label.setText(os.path.basename(file))
        else:
            self.selected_file = None
            self.file_label.setText("No file selected.")
    def process_file(self):
        if not self.selected_file:
            self.output.setText("No file selected.")
            return
        try:
            # Try to use gdalinfo from Python, fallback to subprocess
            try:
                from osgeo import gdal
                ds = gdal.Open(self.selected_file)
                info = gdal.Info(ds)
                # Extract geotransform and projection for InfoBox
                gt = ds.GetGeoTransform()
                proj = ds.GetProjection()
                # Calculate centroid in file CRS
                width = ds.RasterXSize
                height = ds.RasterYSize
                centroid_x = gt[0] + (width / 2) * gt[1]
                centroid_y = gt[3] + (height / 2) * gt[5]
                # Try to detect UTM from proj string
                input_crs = 'wgs84'
                centroid = (centroid_y, centroid_x)
                if 'UTM' in proj or 'PROJCS' in proj:
                    # Try to extract UTM zone and hemisphere
                    import re
                    m = re.search(r'UTM zone (\d+)([A-Z]*)', proj)
                    if m:
                        zone = int(m.group(1))
                        is_north = 'N' in m.group(2) or centroid_y >= 0
                        centroid = (centroid_x, centroid_y, zone, is_north)
                        input_crs = 'utm'
                self.info_box.update_info(centroid, input_crs=input_crs)
            except Exception:
                result = subprocess.run(["gdalinfo", self.selected_file], capture_output=True, text=True)
                info = result.stdout if result.returncode == 0 else result.stderr
                self.info_box.update_info((0,0), input_crs='wgs84')
            self.output.setText(info)
        except Exception as e:
            self.output.setText(f"Error running gdalinfo: {e}")
