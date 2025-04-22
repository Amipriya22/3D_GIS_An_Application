import numpy as np
import rasterio
import pyvista as pv

# Loading our merged DEM 
with rasterio.open("merged.tif") as src:
    dem = src.read(1)
    transform = src.transform

# Cleaning invalid values
dem = np.where((dem <= 0) | (dem > 9000), np.nan, dem)

# Downsampling
step = 30
dem_ds = dem[::step, ::step]
z = np.nan_to_num(dem_ds, nan=0)

# Flood mask: elevation < 500 m
flood_mask = (z < 500).astype(int)

# Coordinate grid
rows, cols = z.shape
x = np.arange(cols) * transform.a * step + transform.c
y = np.arange(rows) * transform.e * step + transform.f
x, y = np.meshgrid(x, y)

# Scaling Z
x_range = np.max(x) - np.min(x)
z_range = np.max(z) - np.min(z)
scale_factor = x_range / z_range if z_range != 0 else 1
z_scaled = (z - np.min(z)) * scale_factor * 0.3

# Creating Grid
grid = pv.StructuredGrid(x, y, z_scaled)
grid.point_data["Flood <500m"] = flood_mask.ravel(order="F")

# Plotting
plotter = pv.Plotter()
plotter.set_background("white")
plotter.add_mesh(grid, scalars="Flood <500m", cmap=["white", "blue"], show_scalar_bar=False)
plotter.add_text("Flood Risk Areas (<500m)", font_size=12)
plotter.camera_position = 'iso'
plotter.camera.zoom(1.5)
plotter.show()
