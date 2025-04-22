import numpy as np
import rasterio
import pyvista as pv

# Loading the merged DEM
with rasterio.open("merged.tif") as src:
    dem = src.read(1)
    transform = src.transform

# Cleaning DEM 
dem = np.where((dem <= 0) | (dem > 9000), np.nan, dem)

# Downsampling
step = 30
dem_ds = dem[::step, ::step]
z = np.nan_to_num(dem_ds, nan=0)

# Generating coordinates
rows, cols = z.shape
x = np.arange(cols) * transform.a * step + transform.c
y = np.arange(rows) * transform.e * step + transform.f
x, y = np.meshgrid(x, y)

#Creating structured grid 
grid = pv.StructuredGrid(x, y, z)

# Flood mask: 1 = flood (<1500m), 0 = safe
flood_mask = (dem_ds < 100) & (dem_ds > 0)
flood_colors = np.where(flood_mask, 1, 0).astype(np.uint8)
grid.point_data.clear()
grid.point_data["Flood Zone"] = flood_colors.ravel(order="F")

# === Plot ===
plotter = pv.Plotter()
plotter.set_background("white")
plotter.add_mesh(grid, scalars="Flood Zone", cmap=["white", "blue"], show_scalar_bar=False)
plotter.add_text("Flood-prone Zones (<1500m)", font_size=12)
plotter.camera_position = 'iso'
plotter.camera.zoom(1.5)
plotter.show()
