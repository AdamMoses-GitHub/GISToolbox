"""
Main GUI window and tab management for Python GIS Data Swiss Army Knife
"""
from PySide6.QtWidgets import QMainWindow, QTabWidget
from tabs.tab_kml_bbox import KMLBoundingBoxTab
from tabs.tab_gdal_info import GDALInfoTab
from tabs.tab_geotiff_display import RasterDisplayTab
from tabs.tab_batch_cut import BatchCutTab

def launch_gui(app):
    window = MainWindow()
    window.show()
    app.exec()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python GIS Data Swiss Army Knife")
        self.resize(900, 700)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.addTab(KMLBoundingBoxTab(self), "Create KML Bounding Box")
        self.tabs.addTab(GDALInfoTab(self), "GDAL Info on File")
        self.tabs.addTab(RasterDisplayTab(self), "Display Raster File (GeoTiff/IMG)")
        self.tabs.addTab(BatchCutTab(self), "Batch Cut")