import streamlit as st
import numpy as np
import rasterio
import pyvista as pv
import tempfile

st.title("Interactive 3D Flood DEM Viewer")

elevation_threshold = st.slider("Select Elevation Threshold (m)", 0, 10, 1000)

# Load DEM (cached)
@st.cache_data
def load_dem():
    with rasterio.open("merged_sea_level.tif") as src:
        dem = src.read(1)
        transform = src.transform
    dem = np.where((dem <= 0) | (dem > 9000), np.nan, dem)
    return dem, transform

dem, transform = load_dem()

# Process DEM
step = 30
dem_ds = dem[::step, ::step]
z = np.nan_to_num(dem_ds, nan=0)
flood_mask = (z < elevation_threshold).astype(int)

rows, cols = z.shape
x = np.arange(cols) * transform.a * step + transform.c
y = np.arange(rows) * transform.e * step + transform.f
x, y = np.meshgrid(x, y)
x_range = np.max(x) - np.min(x)
z_range = np.max(z) - np.min(z)
scale_factor = x_range / z_range if z_range else 1
z_scaled = (z - np.min(z)) * scale_factor * 0.3

grid = pv.StructuredGrid(x, y, z_scaled)
grid.point_data["Flood Mask"] = flood_mask.ravel(order="F")

plotter = pv.Plotter(off_screen=True)
plotter.set_background("white")
plotter.add_mesh(grid, scalars="Flood Mask", cmap=["white", "blue"], show_scalar_bar=False)
plotter.camera_position = 'iso'
plotter.camera.zoom(1.5)


tmp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
plotter.screenshot(tmp_file.name)
st.image(tmp_file.name, caption=f"Flood Risk Zones Below {elevation_threshold}m")

