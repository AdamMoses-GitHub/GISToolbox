"""
Tab 2: GDAL Info on a File
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel
)
from widgets.info_box import InfoBox
import subprocess
import os
import re

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
        # Output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout().addWidget(self.output)
        # Info box
        self.info_box = InfoBox()
        self.layout().addWidget(self.info_box)
        self.selected_file = None

    def choose_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select GIS Raster File",
            "",
            "Raster Files (*.tif *.tiff *.img *.vrt *.asc *.bil *.nc);;All Files (*)"
        )
        if file:
            self.selected_file = file
            self.file_label.setText(os.path.basename(file))
            self.process_file()
        else:
            self.selected_file = None
            self.file_label.setText("No file selected.")
            self.output.clear()
            self.info_box.update_info([], input_crs='wgs84')

    def process_file(self):
        if not self.selected_file:
            self.output.setText("No file selected.")
            self.info_box.update_info([], input_crs='wgs84')
            return

        info = None
        try:
            from osgeo import gdal, osr
            ds = gdal.Open(self.selected_file)
            if ds:
                info = gdal.Info(ds)
                gt = ds.GetGeoTransform()
                proj = ds.GetProjection()
                width = ds.RasterXSize
                height = ds.RasterYSize

                # Calculate bounding box corners
                x0, y0 = gt[0], gt[3]
                x1, y1 = gt[0] + width * gt[1], gt[3] + width * gt[4]
                x2, y2 = gt[0] + width * gt[1] + height * gt[2], gt[3] + width * gt[4] + height * gt[5]
                x3, y3 = gt[0] + height * gt[2], gt[3] + height * gt[5]
                native_corners = [
                    (x0, y0),  # top-left
                    (x1, y1),  # top-right
                    (x2, y2),  # bottom-right
                    (x3, y3)   # bottom-left
                ]

                input_crs = 'wgs84'
                bbox_corners_for_info = []

                if proj:
                    srs = osr.SpatialReference()
                    try:
                        srs.ImportFromWkt(proj)
                        if srs.IsProjected():
                            utm_zone = srs.GetUTMZone()
                            is_north = srs.IsNorth()
                            if utm_zone:
                                input_crs = 'utm'
                                bbox_corners_for_info = [
                                    (x, y, utm_zone, is_north) for (x, y) in native_corners
                                ]
                            else:
                                # Transform corners to WGS84 (lon, lat)
                                target_srs = osr.SpatialReference()
                                target_srs.ImportFromEPSG(4326)
                                coord_transform = osr.CoordinateTransformation(srs, target_srs)
                                bbox_corners_for_info = [
                                    coord_transform.TransformPoint(x, y)[:2][::-1] for (x, y) in native_corners
                                ]
                                input_crs = 'wgs84'
                        elif srs.IsGeographic():
                            bbox_corners_for_info = native_corners
                            input_crs = 'wgs84'
                        else:
                            bbox_corners_for_info = native_corners
                            input_crs = 'wgs84'
                    except Exception as srs_e:
                        print(f"SRS handling failed: {srs_e}. Passing native corners as WGS84 fallback.")
                        bbox_corners_for_info = native_corners
                        input_crs = 'wgs84'
                else:
                    bbox_corners_for_info = native_corners
                    input_crs = 'wgs84'

                self.info_box.update_info(bbox_corners_for_info, input_crs=input_crs)
            else:
                info = "Could not open raster file."
                self.info_box.update_info([], input_crs='wgs84')

        except Exception as e:
            # If osgeo fails, try subprocess
            print(f"osgeo failed: {e}. Falling back to subprocess.")
            try:
                result = subprocess.run(
                    ["gdalinfo", self.selected_file],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                info = result.stdout if result.returncode == 0 else result.stderr

                if result.returncode == 0:
                    # Parse corners from gdalinfo output
                    corner_regex = re.compile(
                        r"(Upper Left|Lower Left|Upper Right|Lower Right):\s+\(\s*([-.\d]+)[,\s]+([-.\d]+)\)"
                    )
                    matches = corner_regex.findall(info)
                    corner_map = {
                        "Upper Left": None,
                        "Upper Right": None,
                        "Lower Right": None,
                        "Lower Left": None
                    }
                    for label, x_str, y_str in matches:
                        corner_map[label] = (float(x_str), float(y_str))
                    if all(corner_map.values()):
                        bbox_from_subprocess = [
                            corner_map["Upper Left"],
                            corner_map["Upper Right"],
                            corner_map["Lower Right"],
                            corner_map["Lower Left"]
                        ]
                        subprocess_input_crs = 'wgs84'
                        bbox_for_info_sub = bbox_from_subprocess
                        if re.search(r'PROJCS\[', info):
                            utm_match = re.search(r'UTM zone (\d+)([NnSs])', info)
                            if utm_match:
                                utm_zone = int(utm_match.group(1))
                                is_north = utm_match.group(2).upper() == 'N'
                                bbox_for_info_sub = [
                                    (x, y, utm_zone, is_north) for (x, y) in bbox_from_subprocess
                                ]
                                subprocess_input_crs = 'utm'
                        self.info_box.update_info(bbox_for_info_sub, input_crs=subprocess_input_crs)
                    else:
                        self.info_box.update_info([], input_crs='wgs84')
                else:
                    self.info_box.update_info([], input_crs='wgs84')
            except Exception as sub_e:
                info = f"An unexpected error occurred: {sub_e}"
                self.info_box.update_info([], input_crs='wgs84')

        # Display the raw gdalinfo output if obtained
        if info is not None:
            self.output.setText(info)
        else:
            self.output.setText("Could not retrieve GDAL info.")
