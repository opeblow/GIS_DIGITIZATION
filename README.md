# Map Digitization Pipeline

A professional raster-to-vector digitization utility that converts georeferenced map rasters into vector features (polygons and lines) by clustering raster colors, cleaning raster masks, extracting contours, and exporting GeoPackage/Shapefile outputs. Built for reproducible, scriptable pre-processing of scanned maps for GIS workflows.

Status: Stable prototype — production-ready for small-to-medium datasets.

---

## Table of Contents

- Project overview
- Real-world use case
- Key features
- Technology stack
- Quick start (virtual environment)
- Usage examples
- Configuration (script-level)
- Project structure
- Troubleshooting & tips
- Development & license

---

## Project overview

This repository contains a single-script pipeline ([`digitization.py`](digitization.py)) that:

- Loads a georeferenced raster from [map_data/](map_data/)
- Clusters pixel colors using KMeans
- Applies morphological cleanup
- Extracts contours and converts them to vector geometries
- Writes per-cluster and merged vector outputs to an output folder

Designed to preserve raster geotransform and CRS when present.

---

## Real-world use case

- Turning scanned or orthorectified historical/topographic map tiles into vector layers for analysis.
- Rapid extraction of map features (roads, water bodies, land cover patches) as a first pass for manual QA in QGIS.
- Pre-processing legacy map archives for migration into GIS databases.

---

## Key features

- Color-based KMeans clustering with progress verbosity.
- Morphological open/close to reduce noise.
- Contour simplification and area-based type decision (polygon vs line).
- CRS preservation and fallback to EPSG:32633 if missing.
- Outputs per-cluster shapefiles and a merged dataset.

---

## Technology stack

- Python 3.x
- rasterio — raster I/O ([requirements.txt](requirements.txt))
- OpenCV (cv2) — image processing
- numpy — numeric arrays
- scikit-learn — KMeans clustering
- geopandas & shapely — vector creation & export

See [requirements.txt](requirements.txt) for pinned packages.

---

## Quick start — virtual environment (recommended)

1. Create a clean virtual environment:

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

(See [requirements.txt](requirements.txt))

3. Ensure your georeferenced raster(s) are in [map_data/](map_data/). The script looks for the base name configured by [`digitization.BASE_NAME`](digitization.py) and the extensions in [`digitization.possible_extensions`](digitization.py).

---

## Usage examples

Run the digitizer with default configuration:

```bash
python digitization.py
```

Example run output (high-level):

- Found raster file: map_data/NARAGUTA SE SHT 1681.tif
- Resized for processing (if large)
- Clustering progress from scikit-learn
- Per-cluster shapefiles written to `output/`
- Merged file: `output/ALL_DIGITIZED_FEATURES.shp`

Open the raster + output shapefiles in QGIS for review.

---

## Configuration (script-level)

Primary knobs live at the top of [`digitization.py`](digitization.py). Edit as needed:

- [`digitization.INPUT_FOLDER`](digitization.py) — input directory (default: `'map_data'`)  
- [`digitization.BASE_NAME`](digitization.py) — raster base filename (default: `'NARAGUTA SE SHT 1681'`)  
- [`digitization.OUTPUT_FOLDER`](digitization.py) — output directory (default: `'output'`)  
- [`digitization.N_CLUSTERS`](digitization.py) — number of KMeans clusters (default: `10`)  
- [`digitization.MIN_AREA`](digitization.py) — min contour area (pixels) to keep (default: `100`)  
- [`digitization.POLYGON_MIN_AREA`](digitization.py) — area threshold to treat contours as polygons (default: `1000`)  
- [`digitization.MORPH_ITER`](digitization.py) — morphological iterations (default: `2`)  
- [`digitization.possible_extensions`](digitization.py) — list of considered file extensions  
- [`digitization.INPUT_FILE`](digitization.py) — resolved input file path (set at runtime)

Adjust these values to control sensitivity, output type, and performance.

---

## Project folder structure

Top-level layout:

- [.gitignore](.gitignore) — ignored patterns (virtualenv, map_data)
- [digitization.py](digitization.py) — main processing script
- [README.md](README.md) — this file
- [requirements.txt](requirements.txt) — Python dependencies
- map_data/ — input rasters and auxiliary georeferencing files
  - NARAGUTA SE SHT 1681.tfw
  - NARAGUTA SE SHT 1681.tif.aux.xml
  - NARAGUTA SE SHT 1681.tif.ovr
- myenv/ — local virtualenv (excluded by .gitignore)

(See repository root for exact items.)

---

## Troubleshooting & tips

- If no raster is found, confirm [`digitization.BASE_NAME`](digitization.py) matches your file base name and that the file extension is in [`digitization.possible_extensions`](digitization.py).
- If few/no features are produced: increase [`digitization.N_CLUSTERS`](digitization.py) or decrease [`digitization.MIN_AREA`](digitization.py).
- For very large rasters the script downsamples; to process full resolution, adjust the resize threshold inside [digitization.py](digitization.py).
- Verify your raster has georeference (TFW/.aux). If missing, the script falls back to EPSG:32633 and prints a warning.

---

## Development & testing

- Use a dedicated virtual environment (see Quick start).
- Reproducibility: pin package versions in [requirements.txt](requirements.txt).
- Outputs are written to the folder specified by [`digitization.OUTPUT_FOLDER`](digitization.py).

---



---

## Files referenced

- [digitization.py](digitization.py) — main script and configuration (see variables like [`digitization.INPUT_FOLDER`](digitization.py), [`digitization.N_CLUSTERS`](digitization.py))
- [requirements.txt](requirements.txt)
- [.gitignore](.gitignore)
- [map_data/](map_data/)
