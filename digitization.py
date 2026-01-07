import rasterio
import cv2
import numpy as np
from shapely.geometry import Polygon, LineString
import geopandas as gpd
import os
from sklearn.cluster import KMeans


INPUT_FOLDER = 'map_data'                     
BASE_NAME = 'NARAGUTA SE SHT 1681'              
OUTPUT_FOLDER = 'output'                         
N_CLUSTERS = 10                               
MIN_AREA = 100                                   
POLYGON_MIN_AREA = 1000                        
MORPH_ITER = 2                   
possible_extensions = ['.tif', '.tiff', '.tif.ovr', '.tfw', '.tif.aux.xml', '.jpg', '.png']
INPUT_FILE = None

for ext in possible_extensions:
    test_path = os.path.join(INPUT_FOLDER, BASE_NAME + ext)
    if os.path.exists(test_path):
        INPUT_FILE = test_path
        print(f"Found raster file: {INPUT_FILE}", flush=True)
        break

if INPUT_FILE is None:
    raise FileNotFoundError(f"Could not find raster file with base name '{BASE_NAME}' in folder '{INPUT_FOLDER}'")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

try:
    with rasterio.open(INPUT_FILE) as src:
        img = src.read().transpose(1, 2, 0)  
        transform = src.transform
        crs = src.crs
        if crs is None:
            from rasterio.crs import CRS
            crs=CRS.from_epsg(32633)
            print(f"Warning:No CRS found,using EPSG:32633")
        height,width=img.shape[:2]

    print(f"Loaded {os.path.basename(INPUT_FILE)} | Size: {width}x{height} | CRS: {crs}", flush=True)
except Exception as e:
    print(f"ERROR opening raster '{INPUT_FILE}': {e}", flush=True)
    raise


if max(height, width) > 5000:
    scale = 5000 / max(height, width)
    new_width = int(width * scale)
    new_height = int(height * scale)
    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
    print(f"Resized to {new_width}x{new_height} for faster processing", flush=True)

pixels = img.reshape(-1, 3).astype(np.float32)

print(f"Clustering {pixels.shape[0]} pixels into {N_CLUSTERS} clusters...", flush=True)
# enable KMeans verbose output so users see progress from sklearn internals
kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10, verbose=1)
kmeans.fit(pixels)
print("Clustering complete.", flush=True)
labels = kmeans.labels_.reshape(img.shape[:2])
cluster_colors = kmeans.cluster_centers_.astype(np.uint8)

all_gdfs = []

print("Processing color clusters...", flush=True)

for i in range(N_CLUSTERS):
    print(f"Processing cluster {i+1}/{N_CLUSTERS} (cluster id {i})...", flush=True)
    mask = (labels == i).astype(np.uint8) * 255
    
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=MORPH_ITER)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=MORPH_ITER)
    
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    geometries = []
    types = []
    color_str = tuple(map(int, cluster_colors[i]))
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_AREA:
            continue
        
        epsilon = 0.001 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, closed=True)
        
      
        geo_coords = [transform * (x, y) for x, y in approx.reshape(-1, 2)]
        
        if area > POLYGON_MIN_AREA and len(geo_coords) >= 4:
            geom = Polygon(geo_coords)
            geometries.append(geom)
            types.append('polygon')
        else:
            geom = LineString(geo_coords)
            geometries.append(geom)
            types.append('line')
    
    if geometries:
        gdf = gpd.GeoDataFrame({
            'geometry': geometries,
            'type': types,
            'cluster': i,
            'color_rgb': str(color_str)
        }, crs=crs)
        
        filename = f"{OUTPUT_FOLDER}/layer_{i:02d}color{color_str}.shp"
        print(f"  Saving cluster {i} → {filename}", flush=True)
        gdf.to_file(filename)
        all_gdfs.append(gdf)
        print(f"  Cluster {i} ({color_str}): {len(gdf)} features → {os.path.basename(filename)}", flush=True)


if all_gdfs:
    merged = gpd.pd.concat(all_gdfs, ignore_index=True)
    merged_filename = f"{OUTPUT_FOLDER}/ALL_DIGITIZED_FEATURES.shp"
    print(f"Saving merged features → {merged_filename}", flush=True)
    merged.to_file(merged_filename)
    print(f"\nSUCCESS! Total features digitized: {len(merged)}", flush=True)
    print(f"All files saved in: {OUTPUT_FOLDER}/", flush=True)
    print(f"Next: Open in QGIS → Load {INPUT_FILE} + output folder → Review & clean up", flush=True)
else:
    print("No features found. Try adjusting N_CLUSTERS or MIN_AREA.", flush=True)

    