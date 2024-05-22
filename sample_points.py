from imports import o3d, np
import matplotlib.pyplot as plt
from helpers import get_plotly_fig

mesh_path = "./sweaterfrog_1step.glb"

mesh = o3d.io.read_triangle_mesh(mesh_path)

# triangles = np.asarray(mesh.triangles)

# downsampled_mesh = mesh.simplify_vertex_clustering(0.05)

# print(triangles.shape)

n_pts = 20_000
pcd = mesh.sample_points_poisson_disk(n_pts)

points = np.asarray(pcd.points)
# colors = np.asarray(pcd.colors)

# calc based on pairwise point distance to find best voxel size

point_pairwise_dist_sq = (points ** 2).sum(axis = 1, keepdims=True) + (points ** 2).sum(axis = 1, keepdims=True).T - 2 * points @ points.T
max_dist = point_pairwise_dist_sq.max()

point_closest_dist = (point_pairwise_dist_sq + np.eye(points.shape[0]) * max_dist).min(axis = 1)

assert point_closest_dist.shape[0] == points.shape[0]

voxel_size = (point_closest_dist.mean() ** 0.5) * 2
print(voxel_size)

voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd,
                                                            voxel_size=voxel_size)

voxels = voxel_grid.get_voxels()  # returns list of voxels
indices = np.stack(list(vx.grid_index for vx in voxels))
colors = np.stack(list(vx.color for vx in voxels)) * 255.

# with open("frog_points.npy", "wb") as points_npy:
# 	np.save(points_npy, indices)

# with open("frog_colors.npy", "wb") as colors_npy:
# 	np.save(colors_npy, colors)

with open("color_index.npy", "rb") as index_npy:
	color_index = np.load(index_npy)

with open("block_ids.npy", "rb") as ids_npy:
	block_ids = np.load(ids_npy)

# A^2 + B^2 - 2AB
color_dist_sq = (colors ** 2).sum(axis = 1, keepdims=True) + (color_index ** 2).sum(axis = 1, keepdims = True).T - 2 * (colors @ color_index.T)

block_indices = np.argmin(color_dist_sq, axis = 1)

assert block_indices.shape[0] == colors.shape[0]

frog_block_ids = np.take_along_axis(block_ids, block_indices, axis = 0)

print(frog_block_ids[:5])
print(frog_block_ids.shape)

with open("frog_blocks.npy", "wb") as blocks_npy:
	np.save(blocks_npy, frog_block_ids)

commands = []

for block_id, (x, y, z) in zip(frog_block_ids, indices):
	# print(x, y, z)
	commands.append(
		f"setblock ~{x} ~{y} ~{z} {block_id}"
	)
	# print(commands[-1])

with open("f.txt", "w") as txt_file:
	txt_file.writelines("\n".join(commands))



# print(points[0:10])
# print(colors[0:10])

# o3d.visualization.draw_geometries([pcd])

# o3d.visualization.draw_geometries([voxel_grid])
	
# viz = o3d.visualization.Visualizer()

# viz.create_window(visible = False)
	
# viz.add_geometry(voxel_grid)

# viz.capture_screen_image("output.png", do_render = True)
	
fig = get_plotly_fig([pcd], front = [-0.12, 0.03, 0])

fig.show()

	# geometry_list,
  #                  width=600,
  #                  height=400,
  #                  mesh_show_wireframe=False,
  #                  point_sample_factor=1,
  #                  front=None,
  #                  lookat=None,
  #                  up=None,
  #                  zoom=1.0

# mat = o3d.visualization.rendering.MaterialRecord()
# mat.shader = 'defaultUnlit'

# renderer_pc = o3d.visualization.rendering.OffscreenRenderer(512, 512)
# renderer_pc.scene.set_background(np.array([0, 0, 0, 0]))
# renderer_pc.scene.add_geometry("voxel", voxel_grid, mat)

# captured_image = np.asarray(renderer_pc.render_to_image())

# normalized_image = (captured_image - captured_image.min()) / (captured_image.max() - captured_image.min())
# plt.imshow(normalized_image)
# plt.savefig('depth.png')
