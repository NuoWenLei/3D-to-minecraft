import streamlit as st
import tempfile
import open3d as o3d
import numpy as np
import json
from helpers import get_plotly_fig

# def convert_3d(filename):
# 	mesh = o3d.io.read_triangle_mesh(filename)
# 	n_pts = 10_000
# 	pcd = mesh.sample_points_poisson_disk(n_pts)
# 	voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd,
#                                                             voxel_size=0.03)
# 	voxels = voxel_grid.get_voxels()  # returns list of voxels
# 	indices = np.stack(list(vx.grid_index for vx in voxels))
# 	colors = np.stack(list(vx.color for vx in voxels)) * 255.

# 	with open("color_index.npy", "rb") as index_npy:
# 		color_index = np.load(index_npy)

# 	with open("block_ids.npy", "rb") as ids_npy:
# 		block_ids = np.load(ids_npy)

# 	# A^2 + B^2 - 2AB
# 	color_dist_sq = (colors ** 2).sum(axis = 1, keepdims=True) + (color_index ** 2).sum(axis = 1, keepdims = True).T - 2 * (colors @ color_index.T)

# 	block_indices = np.argmin(color_dist_sq, axis = 1)

# 	assert block_indices.shape[0] == colors.shape[0]

# 	model_block_ids = np.take_along_axis(block_ids, block_indices, axis = 0)

# 	commands = []

# 	for block_id, (x, y, z) in zip(model_block_ids, indices):
# 		# print(x, y, z)
# 		commands.append(
# 			f"setblock ~{x} ~{y} ~{z} {block_id}"
# 		)
# 		# print(commands[-1])

# 	with open("f.txt", "w") as txt_file:
# 		txt_file.writelines("\n".join(commands))

with open("id2texture.json", "r") as texture_json:
	id2texture = json.load(texture_json)

st.title("3D Model to Minecraft Function Converter")

model_name = st.text_input("Function Name (Optional)", placeholder="e.g. generate_frog")

placeholder = st.empty()

with placeholder:
		uploadedFile = st.file_uploader(
				"Upload a STL, GLB, or OBJ file:",
				["stl", "glb", "obj"],
				accept_multiple_files=False,
				key="fileuploader",
		)

if uploadedFile:
	# st.button("Convert", on_click=)
	with st.spinner("Generating Function Commands..."):
		with tempfile.NamedTemporaryFile(suffix="_streamlit" + "." + uploadedFile.name.split(".")[-1]) as f:
			f.write(uploadedFile.getbuffer())
			mesh = o3d.io.read_triangle_mesh(f.name)

		n_pts = 10_000
		pcd = mesh.sample_points_poisson_disk(n_pts)
		points = np.asarray(pcd.points)
		point_pairwise_dist_sq = (points ** 2).sum(axis = 1, keepdims=True) + (points ** 2).sum(axis = 1, keepdims=True).T - 2 * points @ points.T
		max_dist = point_pairwise_dist_sq.max()

		point_closest_dist = (point_pairwise_dist_sq + np.eye(points.shape[0]) * max_dist).min(axis = 1)

		plotly_fig = get_plotly_fig([mesh, pcd])

		assert point_closest_dist.shape[0] == points.shape[0]

		voxel_size = (point_closest_dist.mean() ** 0.5) * 2
		voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd,
																															voxel_size=voxel_size)
		voxels = voxel_grid.get_voxels()  # returns list of voxels
		indices = np.stack(list(vx.grid_index for vx in voxels))
		colors = np.stack(list(vx.color for vx in voxels)) * 255.

		with open("color_index.npy", "rb") as index_npy:
			color_index = np.load(index_npy)

		with open("block_ids.npy", "rb") as ids_npy:
			block_ids = np.load(ids_npy)

		# A^2 + B^2 - 2AB
		color_dist_sq = (colors ** 2).sum(axis = 1, keepdims=True) + (color_index ** 2).sum(axis = 1, keepdims = True).T - 2 * (colors @ color_index.T)

		block_indices = np.argmin(color_dist_sq, axis = 1)

		assert block_indices.shape[0] == colors.shape[0]

		model_block_ids = np.take_along_axis(block_ids, block_indices, axis = 0)

		unique_blocks, block_counts = np.unique(model_block_ids, return_counts = True)

		block_usages = sorted(zip(unique_blocks, block_counts), key = lambda x : x[1], reverse=True)

		# st.table

		n = min(5, len(unique_blocks))

		st.subheader(f"Top {n} Block Usages")
		cols = st.columns(n)

		for i in range(n):
			cols[i].image(f"textures/{id2texture[block_usages[i][0]]}")
			cols[i].caption(f"Block '{block_usages[i][0].split(':')[1]}' is used {block_usages[i][1]} times")

		commands = []
		
		st.subheader("Mesh Visualization")
		print("this ran again")
		st.plotly_chart(plotly_fig)
		"&nbsp;"
		axes = {
			"x": 0,
			"y": 1,
			"z": 2
		}
		height_axis_text = st.radio("Set the height axis (what direction is up for the mesh)", ["x", "y", "z"], index = 1)
		# height_axis = int(height_axis_text)
		height_axis = axes[height_axis_text]
		print(height_axis_text)
		for block_id, xyz in zip(model_block_ids, indices):
			x, y, z = xyz[(height_axis - 1) % 3], xyz[height_axis], xyz[(height_axis + 1) % 3]
			commands.append(
				f"setblock ~{-x} ~{y} ~{-z} {block_id}"
			)
		st.download_button(
			"Download Minecraft Function file",
			"\n".join(commands),
			file_name = f"{model_name}.mcfunction" if model_name is not None else "generate_model.mcfunction")
