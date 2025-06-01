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
import re # Import re for UTM zone detection

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
            self.process_file()  # Automatically display after file selection
        else:
            self.selected_file = None
            self.file_label.setText("No file selected.")
            self.stats_box.clear()
            self.info_box.update_info([(0,0),(0,0),(0,0),(0,0)], input_crs='wgs84')
            self.ax.clear()
            self.canvas.draw()

    def process_file(self):
        if not self.selected_file:
            self.stats_box.setText("No file selected.")
            self.info_box.update_info([(0,0),(0,0),(0,0),(0,0)], input_crs='wgs84') # Reset info box
            self.ax.clear()
            self.canvas.draw()
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
            # Info box: extract bounding box and CRS
            gt = ds.GetGeoTransform()
            proj = ds.GetProjection()
            width = ds.RasterXSize
            height = ds.RasterYSize

            # (0,0) pixel is top-left
            x0, y0 = gt[0], gt[3]
            # (width, 0) pixel is top-right
            x1, y1 = gt[0] + width * gt[1], gt[3] + width * gt[4]
            # (width, height) pixel is bottom-right
            x2, y2 = gt[0] + width * gt[1] + height * gt[2], gt[3] + width * gt[4] + height * gt[5]
            # (0, height) pixel is bottom-left
            x3, y3 = gt[0] + height * gt[2], gt[3] + height * gt[5]

            # Bounding box as (top-left, top-right, bottom-right, bottom-left)
            bbox = [
                (x0, y0),      # top-left
                (x1, y1),      # top-right
                (x2, y2),      # bottom-right
                (x3, y3)       # bottom-left
            ]

            # Try to detect UTM from proj string
            input_crs = 'wgs84' # Default to wgs84 if not UTM
            if 'UTM' in proj or 'PROJCS' in proj:
                m = re.search(r'UTM zone (\d+)([NnSs])', proj)
                if m:
                    zone = int(m.group(1))
                    is_north = m.group(2).upper() == 'N'
                    bbox = [(x, y, zone, is_north) for (x, y) in bbox]
                    input_crs = 'utm'

            self.info_box.update_info(bbox, input_crs=input_crs)

        except Exception as e:
            self.stats_box.setText(f"Error displaying raster: {e}")
            self.info_box.update_info([(0,0),(0,0),(0,0),(0,0)], input_crs='wgs84')
            self.ax.clear()
            self.canvas.draw()
