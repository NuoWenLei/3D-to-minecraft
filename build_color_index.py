import json
import numpy as np

with open("valid_blocks.json", "r") as terracotta_json:
	terracotta = json.load(terracotta_json)

colors = []
ids = []

id2texture = dict()

for block in terracotta:
	colors.append([
		block["red"], block["green"], block["blue"]
	])

	ids.append(block["game_id"])
	id2texture[block["game_id"]] = block["texture_image"]

colors = np.array(colors)
ids = np.array(ids)

with open("id2texture.json", "w") as texture_json:
	json.dump(id2texture, texture_json)

with open("color_index.npy", "wb") as color_index_npy:
	np.save(color_index_npy, colors)

with open("block_ids.npy", "wb") as id_npy:
	np.save(id_npy, ids)