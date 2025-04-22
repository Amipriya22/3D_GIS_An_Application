import numpy as np
import rasterio
import pyvista as pv

# === Load DEM ===
with rasterio.open("merged.tif") as src:
    dem = src.read(1)
    transform = src.transform

# === Clean & Downsample ===
dem = np.where((dem <= 0) | (dem > 9000), np.nan, dem)
step = 30
dem_ds = dem[::step, ::step]
z = np.nan_to_num(dem_ds, nan=0)

# === Coordinates ===
rows, cols = z.shape
x = np.linspace(0, cols * step, cols)
y = np.linspace(0, rows * step, rows)
x, y = np.meshgrid(x, y)
z_scaled = z * 5

# === Create Surface ===
points = np.c_[x.ravel(), y.ravel(), z_scaled.ravel()]
mesh = pv.PolyData(points).delaunay_2d()

# === Plotter Setup ===
plotter = pv.Plotter(off_screen=True)
plotter.set_background("white")
plotter.open_movie("terrain_flyin.mp4", framerate=20)
plotter.add_mesh(mesh, color="lightgray")

# === Fly-in / Fly-out camera motion ===
zoom_type = "in"  # choose: "in" or "out"
n_frames = 100
center = mesh.center

start_z = z_scaled.max() * 2
end_z = z_scaled.max() * 0.2    

if zoom_type == "in":
    z_traj = np.linspace(start_z, end_z, n_frames)
else:
    z_traj = np.linspace(end_z, start_z, n_frames)

for z_pos in z_traj:
    plotter.camera_position = [(center[0], center[1], z_pos), center, (0, 1, 0)]
    plotter.render()
    plotter.write_frame()

plotter.close()
