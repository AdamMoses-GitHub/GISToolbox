"""
Tab: Batch Cut by Extent
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QFileDialog,
    QLabel, QLineEdit, QMessageBox, QListWidgetItem, QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import Qt
from datetime import datetime
import os

from widgets.info_box import InfoBox
from osgeo import gdal, ogr, osr
from shapely.geometry import box, shape, mapping
from shapely.ops import unary_union
from pyproj import CRS, Transformer

class BatchCutTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Input files list
        self.input_list = QListWidget()
        self.input_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        layout.addWidget(QLabel("Input Raster/Vector Files:"))
        layout.addWidget(self.input_list)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Files")
        self.remove_btn = QPushButton("Remove Selected")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.add_files)
        self.remove_btn.clicked.connect(self.remove_selected_files)

        # Cut file
        cut_layout = QHBoxLayout()
        self.cut_file_edit = QLineEdit()
        self.cut_file_edit.setReadOnly(True)
        self.cut_file_btn = QPushButton("Select Cut File")
        cut_layout.addWidget(QLabel("Cut File:"))
        cut_layout.addWidget(self.cut_file_edit)
        cut_layout.addWidget(self.cut_file_btn)
        layout.addLayout(cut_layout)
        self.cut_file_btn.clicked.connect(self.select_cut_file)

        # Output directory
        out_layout = QHBoxLayout()
        self.out_dir_edit = QLineEdit()
        self.out_dir_edit.setReadOnly(True)
        self.out_dir_btn = QPushButton("Select Output Directory")
        out_layout.addWidget(QLabel("Output Directory:"))
        out_layout.addWidget(self.out_dir_edit)
        out_layout.addWidget(self.out_dir_btn)
        layout.addLayout(out_layout)
        self.out_dir_btn.clicked.connect(self.select_output_dir)

        # Postfix
        postfix_layout = QHBoxLayout()
        self.postfix_edit = QLineEdit()
        default_postfix = datetime.now().strftime("_%Y%m%d_%H%M%S")
        self.postfix_edit.setText(default_postfix)
        postfix_layout.addWidget(QLabel("Filename Postfix:"))
        postfix_layout.addWidget(self.postfix_edit)
        layout.addLayout(postfix_layout)

        # Process button
        self.process_btn = QPushButton("Process Batch Cut")
        layout.addWidget(self.process_btn)
        self.process_btn.clicked.connect(self.process_batch_cut)

        layout.addStretch()

        # InfoBox for cut file
        self.info_box = InfoBox()
        self.info_box.setMinimumHeight(140)
        self.info_box.setMaximumHeight(200)
        self.info_box.setSizePolicy(self.info_box.sizePolicy().horizontalPolicy(), QSizePolicy.Fixed)
        layout.addWidget(self.info_box)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Input Files", "", "All Files (*.*)")
        for f in files:
            if f and not any(self.input_list.item(i).text() == f for i in range(self.input_list.count())):
                self.input_list.addItem(QListWidgetItem(f))

    def remove_selected_files(self):
        for item in self.input_list.selectedItems():
            self.input_list.takeItem(self.input_list.row(item))

    def select_cut_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Cut File", "", "All Files (*.*)")
        if file:
            self.cut_file_edit.setText(file)
            self.update_cut_info_box(file)

    def select_output_dir(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Output Directory", "")
        if dir:
            self.out_dir_edit.setText(dir)

    def process_batch_cut(self):
        input_files = [self.input_list.item(i).text() for i in range(self.input_list.count())]
        cut_file = self.cut_file_edit.text()
        out_dir = self.out_dir_edit.text()
        postfix = self.postfix_edit.text()

        if not input_files or not cut_file or not out_dir:
            QMessageBox.warning(self, "Missing Info", "Please select input files, a cut file, and an output directory.")
            return

        # Get cut geometry and CRS
        cut_geom, cut_crs = self.get_cut_geometry_and_crs(cut_file)
        if cut_geom is None or cut_crs is None:
            QMessageBox.warning(self, "Error", "Could not determine geometry or CRS of cut file.")
            return

        failed = []
        for in_file in input_files:
            base = os.path.splitext(os.path.basename(in_file))[0]
            ext = os.path.splitext(in_file)[1]
            out_file = os.path.join(out_dir, f"{base}{postfix}{ext}")

            try:
                if self.is_raster(in_file):
                    self.cut_raster(in_file, out_file, cut_geom, cut_crs)
                else:
                    self.cut_vector(in_file, out_file, cut_geom, cut_crs)
            except Exception as e:
                failed.append((in_file, str(e)))

        if failed:
            msg = "Some files failed to process:\n"
            for f, err in failed:
                msg += f"{os.path.basename(f)}: {err}\n"
            QMessageBox.warning(self, "Batch Cut", msg)
        else:
            QMessageBox.information(self, "Batch Cut", "Batch cut operation completed successfully.")

    def is_raster(self, filename):
        raster_exts = (".tif", ".tiff", ".img", ".vrt", ".asc", ".bil", ".nc")
        ext = os.path.splitext(filename)[1].lower()
        if ext in raster_exts:
            return True
        try:
            ds = gdal.Open(filename)
            if ds:
                return True
        except Exception:
            pass
        return False

    def get_cut_geometry_and_crs(self, cut_file):
        # Try raster first
        ds = gdal.Open(cut_file)
        if ds:
            gt = ds.GetGeoTransform()
            width = ds.RasterXSize
            height = ds.RasterYSize
            proj = ds.GetProjection()
            # Four corners
            x0, y0 = gt[0], gt[3]
            x1, y1 = gt[0] + width * gt[1], gt[3] + width * gt[4]
            x2, y2 = gt[0] + width * gt[1] + height * gt[2], gt[3] + width * gt[4] + height * gt[5]
            x3, y3 = gt[0] + height * gt[2], gt[3] + height * gt[5]
            geom = box(min(x0, x1, x2, x3), min(y0, y1, y2, y3), max(x0, x1, x2, x3), max(y0, y1, y2, y3))
            crs = CRS.from_wkt(proj) if proj else None
            return geom, crs

        # Try vector
        ds = ogr.Open(cut_file)
        if ds:
            lyr = ds.GetLayer(0)
            srs = lyr.GetSpatialRef()
            crs = CRS.from_wkt(srs.ExportToWkt()) if srs else None
            geoms = []
            for feat in lyr:
                geom = shape(feat.GetGeometryRef().__geo_interface__)
                geoms.append(geom)
            if geoms:
                union = unary_union(geoms)
                return union, crs
        return None, None

    def cut_raster(self, in_file, out_file, cut_geom, cut_crs):
        # Open input raster
        ds = gdal.Open(in_file)
        if ds is None:
            raise Exception("Could not open raster.")
        proj = ds.GetProjection()
        in_crs = CRS.from_wkt(proj) if proj else None

        # Transform cut_geom to raster CRS if needed
        if in_crs and cut_crs and in_crs != cut_crs:
            transformer = Transformer.from_crs(cut_crs, in_crs, always_xy=True)
            cut_geom = self.transform_geom(cut_geom, transformer)

        # Get bbox of cut_geom in raster CRS
        minx, miny, maxx, maxy = cut_geom.bounds

        # Use gdal.Warp for cropping
        warp_opts = gdal.WarpOptions(
            outputBounds=(minx, miny, maxx, maxy),
            cropToCutline=True,
            cutlineDSName=None,
            cutlineLayer=None,
            cutlineWkt=cut_geom.wkt
        )
        result = gdal.Warp(out_file, in_file, options=warp_opts)
        if result is None:
            raise Exception("gdal.Warp failed.")

    def cut_vector(self, in_file, out_file, cut_geom, cut_crs):
        # Open input vector
        ds = ogr.Open(in_file)
        if ds is None:
            raise Exception("Could not open vector.")
        lyr = ds.GetLayer(0)
        srs = lyr.GetSpatialRef()
        in_crs = CRS.from_wkt(srs.ExportToWkt()) if srs else None

        # Transform cut_geom to vector CRS if needed
        if in_crs and cut_crs and in_crs != cut_crs:
            transformer = Transformer.from_crs(cut_crs, in_crs, always_xy=True)
            cut_geom = self.transform_geom(cut_geom, transformer)

        # Create output datasource
        driver = ogr.GetDriverByName("ESRI Shapefile")
        if os.path.exists(out_file):
            driver.DeleteDataSource(out_file)
        out_ds = driver.CreateDataSource(out_file)
        out_lyr = out_ds.CreateLayer(lyr.GetName(), srs, lyr.GetGeomType())

        # Copy fields
        in_layer_defn = lyr.GetLayerDefn()
        for i in range(in_layer_defn.GetFieldCount()):
            field_defn = in_layer_defn.GetFieldDefn(i)
            out_lyr.CreateField(field_defn)

        # Clip features
        for feat in lyr:
            geom = shape(feat.GetGeometryRef().__geo_interface__)
            clipped = geom.intersection(cut_geom)
            if not clipped.is_empty:
                out_feat = ogr.Feature(out_lyr.GetLayerDefn())
                for i in range(in_layer_defn.GetFieldCount()):
                    out_feat.SetField(in_layer_defn.GetFieldDefn(i).GetNameRef(), feat.GetField(i))
                out_feat.SetGeometry(ogr.CreateGeometryFromWkb(clipped.wkb))
                out_lyr.CreateFeature(out_feat)
                out_feat = None
        out_ds = None

    def transform_geom(self, geom, transformer):
        # Transform a shapely geometry using a pyproj Transformer
        def _transform(x, y, z=None):
            return transformer.transform(x, y)
        return shapely.ops.transform(_transform, geom)

    def update_cut_info_box(self, file_path):
        # Try to open as raster with GDAL
        info = None
        try:
            ds = gdal.Open(file_path)
            if ds:
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

                bbox = [
                    (x0, y0),      # top-left
                    (x1, y1),      # top-right
                    (x2, y2),      # bottom-right
                    (x3, y3)       # bottom-left
                ]

                input_crs = 'wgs84'
                native_crs_str = None
                if proj:
                    srs = osr.SpatialReference()
                    try:
                        srs.ImportFromWkt(proj)
                        native_crs_str = srs.ExportToPrettyWkt()
                        if srs.IsProjected():
                            utm_zone = srs.GetUTMZone()
                            is_north = srs.IsNorth()
                            if utm_zone:
                                input_crs = 'utm'
                                bbox = [(x, y, utm_zone, is_north) for (x, y) in bbox]
                        # else: keep as wgs84
                    except Exception:
                        pass
                self.info_box.update_info(bbox, input_crs=input_crs, native_crs=native_crs_str)
                return
        except Exception:
            pass

        # If not raster, clear or show minimal info
        self.info_box.update_info([], input_crs='wgs84', native_crs=None)
