# Python GIS Data Swiss Army Knife

Welcome to the Swiss Army Knife of GIS data! This is your all-in-one, slightly over-caffeinated desktop tool for wrangling, inspecting, and visualizing GIS raster and vector data. Whether you want to make a KML bounding box, peek inside a GeoTiff, or just find out which major city is closest to your data, this app has you covered (and then some).

## What does it do?
- **Tab 1:** Create a KML bounding box (with optional shapefile export!) around any point you like, in UTM or lat/lon. It even tells you the nearest major city, so you know if you’re in the right neighborhood.
- **Tab 2:** Run `gdalinfo` on any raster file and see all the juicy metadata, plus a live sanity-check info box.
- **Tab 3:** Display any GeoTiff or IMG raster file with a rainbow color map, and get instant stats. (Because who doesn’t love rainbows and stats?)

## Setup (Windows, Mac, Linux)
1. **Install Python 3.9+** (if you don’t have it):  
   [Download Python](https://www.python.org/downloads/)
2. **Clone this repo:**
   ```
   git clone https://github.com/yourusername/gis-swiss-army-knife.git
   cd gis-swiss-army-knife
   ```
3. **Install dependencies:**
   ```
   pip install PySide6 GDAL pyproj shapely matplotlib
   ```
   - If you get errors with GDAL, try:
     - `pip install wheel` first
     - Or see [GDAL Windows wheels](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal)

## Running the App
Just run:
```
python main.py
```
If you’re missing any dependencies, the app will pop up a helpful (and slightly judgy) message telling you what to install.

## FAQ
- **Q:** Why does it tell me to install stuff?  
  **A:** Because you need it! GIS is hard, but this app tries to make it easier.
- **Q:** Why does it show the nearest city?  
  **A:** Because it can. And because it’s fun.
- **Q:** Can I use this for serious GIS work?  
  **A:** Sure! But don’t blame us if you start having too much fun.

## License
MIT. Use it, break it, fork it, improve it. Just don’t blame us if you accidentally make a bounding box around Area 51.

---

*Made with love, caffeine, and a little bit of geospatial magic.*
