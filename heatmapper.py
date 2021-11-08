import geopandas as gpd
import pandas as pd
import requests
import glob
import os
import numpy as np
from shapely.geometry import Polygon
import tqdm

import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from scipy.ndimage import gaussian_filter

# In the path you specify below, include the two subfolders:
#  - AOI folder for your area of interest shapefile
#  - Constraints folder, with subfolders titled by the constraint level (must be int)
#  - Within each constraint subfolder place the shapefiles that constitute that constraint level, if there is
#       only 1 place all under 1

path = "C:\\dev\\hacker scripts\\heatmapper\\data\\"


shape = 1000, 1000  # outraster resolution
pnt_constrain_buffer = 1
grid_cells = 100

smoothing = 1  # gaussian sigma factor
constraint_multiplier = 1   # think of it like contrast for degree of constraint

def compileConstraints():
    features_in_aoi = []
    for constraint_path in tqdm.tqdm(constraint_paths):
        constraint = gpd.read_file(constraint_path)
        if aoi.crs != constraint.crs:
            constraint.to_crs(aoi.crs)
        constraint = constraint.explode()
        if "Point" in list(constraint.geom_type):
            constraint['geometry'] = constraint['geometry'].buffer(pnt_constrain_buffer)
        features_in_aoi.append(gpd.clip(constraint, aoi).assign(weight=constraint_path.split("Constraints\\")[1].split("\\")[0]))# .reset_index(drop=True))

    features = pd.concat(features_in_aoi, ignore_index=True)
    return features

def generateGrid(area, cells):
    xmin, ymin, xmax, ymax = area.total_bounds
    x = np.linspace(xmin, xmax, num=cells)
    square_grid_correction = int((ymax - ymin) / (int((xmax - xmin) / len(x))))
    y = np.linspace(ymin, ymax, num=square_grid_correction)
    print(f"X grid spacing: {str((xmax-xmin)/len(x))}")
    print(f"Y grid spacing: {str((ymax-ymin)/len(y))}")

    polygons=[]
    points=[]
    print("creating grid...")
    for i in tqdm.tqdm(range(len(x)-1)):
        for j in range(len(y)-1):
            cell = Polygon([(x[i], y[j]), (x[i + 1], y[j]), (x[i + 1], y[j + 1]), (x[i], y[j + 1])])
            polygons.append(cell)
            points.append(cell.centroid)

    polyGrid = gpd.GeoDataFrame({'geometry': polygons}, crs=area.crs).set_crs(area.crs)
    polypoints = gpd.GeoDataFrame({'geometry': points}, crs=area.crs).set_crs(area.crs)
    # polyGrid.to_file(os.path.join(path, "grid.shp"))
    return polyGrid

def rasterise(heatmap, aoi):
    transform = rasterio.transform.from_bounds(*aoi['geometry'].buffer(2000).total_bounds, *shape)
    ras = rasterize(
        [(row[1]['geometry'], row[1]['weight']) for row in heatmap.iterrows()],
        out_shape=shape,
        transform=transform,
        fill=0,
        all_touched=True,
        dtype=rasterio.uint8)

    ras = gaussian_filter(ras * constraint_multiplier, sigma=smoothing)
    with rasterio.open(
            os.path.join(path, 'raster_heatmap.tif'), 'w',
            driver='GTiff',
            dtype=ras.dtype,
            count=1,
            width=shape[0],
            height=shape[1],
            transform=transform,
            crs=heatmap.crs
    ) as dst:
        dst.write(ras, indexes=1)

if __name__ == "__main__":
    print("running...")
    aoi = gpd.read_file(glob.glob(os.path.join(path, r"AOI\*.shp"))[0])
    constraint_paths = glob.glob(os.path.join(path, r"Constraints\*\*.shp"))

    print("Formatting constraints...")
    constraints = compileConstraints()
    constraints["weight"] = constraints["weight"].apply(lambda w: int(w))
    constraints.to_file(os.path.join(path, "simplified_constraints_data.shp"))

    print("Creating heatmap...")
    constraints = gpd.read_file(os.path.join(path, "simplified_constraints_data.shp"))
    constraints = constraints.drop(
        columns=[ite for ite in list(constraints.columns) if ite not in ["geometry", "weight"]])
    constraints = constraints.explode().reset_index(drop=True)

    # simply rasterising the contraints doesn't account for overlapping constraints, so we create the grid
    print("Creating gridded heatmap...")
    grid = generateGrid(aoi, grid_cells)
    grid_heat = grid
    for weight in tqdm.tqdm([int(i) for i in list(constraints['weight'].unique())]):
        temp = constraints.where(constraints['weight'] == weight).copy()
        temp['weight_'+str(weight)] = temp['weight']
        temp.drop(['weight'], axis=1, inplace=True)
        if 'index_right' in list(grid_heat.columns):
            grid_heat.drop(['index_right'], axis=1, inplace=True)
        grid_heat = gpd.sjoin(grid_heat, temp, how='left', op='intersects')
    sum_cols = [col for col in list(grid_heat.columns) if col.startswith('weight')]
    grid_heat['weight'] = grid_heat[sum_cols].sum(axis=1)
    grid_heat.drop(sum_cols, axis=1, inplace=True)
    grid_heat.to_file(os.path.join(path, "grid_heatmap.shp"))

    rasterise(grid_heat, aoi)



