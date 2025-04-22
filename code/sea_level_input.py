import numpy as np
import rasterio
import pyvista as pv


with rasterio.open("merged_sea_level.tif") as src:
    dem = src.read(1)
    transform = src.transform


dem = np.where((dem <= 0) | (dem > 9000), np.nan, dem)


step = 30
dem_ds = dem[::step, ::step]
z = np.nan_to_num(dem_ds, nan=0)


rows, cols = z.shape
x = np.arange(cols) * transform.a * step + transform.c
y = np.arange(rows) * transform.e * step + transform.f
x, y = np.meshgrid(x, y)


x_range = np.max(x) - np.min(x)
z_range = np.max(z) - np.min(z)
scale_factor = x_range / z_range if z_range != 0 else 1
z_scaled = (z - np.min(z)) * scale_factor * 0.3


grid = pv.StructuredGrid(x, y, z_scaled)


cmap_list = [
    ["white", "blue"],
    ["gray", "black"],
    ["red", "green"],
    ["yellow", "blue"]
]
cmap_names = ["White-Blue", "Gray-Black", "Red-Green", "Yellow-Blue"]
current_cmap_index = [0]
current_threshold = [1000]


plotter = pv.Plotter()
plotter.set_background("white")


def get_mask(thresh):
    return (z < thresh).astype(int)

mask = get_mask(current_threshold[0])
grid.point_data["FloodMask"] = mask.ravel(order="F")
mesh = plotter.add_mesh(grid, scalars="FloodMask", cmap=cmap_list[current_cmap_index[0]], show_scalar_bar=False)
plotter.add_text(f"Flood < {current_threshold[0]}m\nColormap: {cmap_names[current_cmap_index[0]]}", name="label", font_size=10)


def update_threshold(value):
    current_threshold[0] = int(value)
    new_mask = get_mask(current_threshold[0])
    grid.point_data["FloodMask"] = new_mask.ravel(order="F")
    mesh.update_scalars(grid.point_data["FloodMask"])
    plotter.add_text(f"Flood < {current_threshold[0]}m\nColormap: {cmap_names[current_cmap_index[0]]}", name="label", font_size=10)

def update_colormap(index):
    current_cmap_index[0] = int(index)
    plotter.remove_actor(mesh)
    new_mask = get_mask(current_threshold[0])
    grid.point_data["FloodMask"] = new_mask.ravel(order="F")
    plotter.add_mesh(grid, scalars="FloodMask", cmap=cmap_list[current_cmap_index[0]], show_scalar_bar=False)
    plotter.add_text(f"Flood < {current_threshold[0]}m\nColormap: {cmap_names[current_cmap_index[0]]}", name="label", font_size=10)
    plotter.render()


plotter.add_slider_widget(update_threshold, [0, 100], value=current_threshold[0],
                          title="Flood Elevation Threshold", pointa=(.025, .1), pointb=(.4, .1), style='modern')

plotter.add_slider_widget(update_colormap, [0, 3], value=0,
                          title="Colormap Index (0–3)", pointa=(.6, .9), pointb=(.975, .9), style='modern')

plotter.camera_position = 'iso'
plotter.camera.zoom(1.5)
plotter.show()
