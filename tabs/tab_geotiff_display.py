"""
Tab 3: Display Raster File (GeoTiff/IMG)
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit)
from PySide6.QtCore import Qt
from widgets.info_box import InfoBox
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os

class RasterDisplayTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        # File chooser
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected.")
        self.choose_btn = QPushButton("Choose Raster File")
        self.choose_btn.clicked.connect(self.choose_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.choose_btn)
        self.layout().addLayout(file_layout)
        # Process button
        self.process_btn = QPushButton("Display Raster")
        self.process_btn.clicked.connect(self.process_file)
        self.layout().addWidget(self.process_btn)
        # Map display
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout().addWidget(self.canvas)
        # Statistics box
        self.stats_box = QTextEdit()
        self.stats_box.setReadOnly(True)
        self.layout().addWidget(self.stats_box)
        # Info box
        self.info_box = InfoBox()
        self.layout().addWidget(self.info_box)
        self.selected_file = None
    def choose_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Raster File", "", "Raster Files (*.tif *.tiff *.img);;All Files (*)")
        if file:
            self.selected_file = file
            self.file_label.setText(os.path.basename(file))
        else:
            self.selected_file = None
            self.file_label.setText("No file selected.")
    def process_file(self):
        if not self.selected_file:
            self.stats_box.setText("No file selected.")
            return
        try:
            ds = gdal.Open(self.selected_file)
            band = ds.GetRasterBand(1)
            arr = band.ReadAsArray()
            arr = np.ma.masked_invalid(arr)
            vmin, vmax = arr.min(), arr.max()
            self.ax.clear()
            im = self.ax.imshow(arr, cmap='rainbow', vmin=vmin, vmax=vmax)
            self.figure.colorbar(im, ax=self.ax, orientation='vertical')
            self.ax.set_title("Raster Display")
            self.canvas.draw()
            # Stats
            stats = f"Min: {vmin}\nMax: {vmax}\nMean: {arr.mean()}\nStd: {arr.std()}\nShape: {arr.shape}"
            self.stats_box.setText(stats)
            # Info box: extract centroid and CRS
            gt = ds.GetGeoTransform()
            proj = ds.GetProjection()
            width = ds.RasterXSize
            height = ds.RasterYSize
            centroid_x = gt[0] + (width / 2) * gt[1]
            centroid_y = gt[3] + (height / 2) * gt[5]
            input_crs = 'wgs84'
            centroid = (centroid_y, centroid_x)
            if 'UTM' in proj or 'PROJCS' in proj:
                import re
                m = re.search(r'UTM zone (\d+)([A-Z]*)', proj)
                if m:
                    zone = int(m.group(1))
                    is_north = 'N' in m.group(2) or centroid_y >= 0
                    centroid = (centroid_x, centroid_y, zone, is_north)
                    input_crs = 'utm'
            self.info_box.update_info(centroid, input_crs=input_crs)
        except Exception as e:
            self.stats_box.setText(f"Error displaying raster: {e}")
