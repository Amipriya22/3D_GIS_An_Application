import numpy as np
import rasterio
import pyvista as pv

# Loading DEM 
with rasterio.open("merged_sea_level.tif") as src:
    dem = src.read(1)
    transform = src.transform

# Clean and masking
dem = np.where((dem <= 0) | (dem > 9000), np.nan, dem)
sea_rise_threshold = 3 # meters
mask = dem < sea_rise_threshold

# Downsampling
step = 30

dem_ds = dem[::step, ::step]
mask_ds = mask[::step, ::step]
z = np.nan_to_num(dem_ds, nan=0)

# Coordinates  
rows, cols = z.shape
x = np.arange(cols) * transform.a * step + transform.c
y = np.arange(rows) * transform.e * step + transform.f
x, y = np.meshgrid(x, y)

# Fixing vertical exaggeration
x_range = np.max(x) - np.min(x)
z_range = np.max(z) - np.min(z)
scale_factor = x_range / z_range if z_range != 0 else 1
z_scaled = (z - np.min(z)) * scale_factor * 0.3

#Creating Grid
grid = pv.StructuredGrid(x, y, z_scaled)

# Applying sea level mask
colors = np.where(mask_ds, 1, 0)

# Plotting
plotter = pv.Plotter()
plotter.set_background("white")
plotter.add_mesh(grid, scalars=colors, cmap=["lightgray", "blue"], show_scalar_bar=False)
plotter.add_text("Sea Level Rise Risk (<3m)", font_size=12)
plotter.camera_position = 'iso'
plotter.camera.zoom(1.5)
plotter.show()
