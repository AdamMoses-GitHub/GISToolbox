"""
Python GIS Data Swiss Army Knife
Entry point. Checks dependencies and launches the main GUI.
"""
import sys
import importlib
from PySide6.QtWidgets import QApplication, QMessageBox

REQUIRED_MODULES = [
    ("PySide6", "pip install PySide6"),
    ("osgeo", "pip install GDAL"),
    ("pyproj", "pip install pyproj"),
    ("shapely", "pip install shapely"),
    ("matplotlib", "pip install matplotlib"),
]

def check_dependencies():
    missing = []
    for mod, install in REQUIRED_MODULES:
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append((mod, install))
    return missing

def show_missing_dialog(missing):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Missing Dependencies")
    text = "The following Python modules are required but missing:\n\n"
    for mod, install in missing:
        text += f"- {mod} (install with: {install})\n"
    text += "\nPlease install them and restart the application."
    msg.setText(text)
    msg.exec()

def main():
    app = QApplication(sys.argv)
    missing = check_dependencies()
    if missing:
        show_missing_dialog(missing)
        sys.exit(1)
    from gui_main import launch_gui
    launch_gui(app)

if __name__ == "__main__":
    main()
