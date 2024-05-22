import json
from PIL import Image
import numpy as np

with open("blocks_12.json", "r") as blocks_json:
	blocks = json.load(blocks_json)

for block in blocks:
	im = Image.open(f"textures/{block['texture_image']}")
	num_pixels = im.size[0] * im.size[1]
	avg_rgb = np.asarray(im).sum(axis = 0).sum(axis = 0) / num_pixels
	print(block["name"])
	print(avg_rgb)
	block["red"] = int(avg_rgb[0])
	block["green"] = int(avg_rgb[1])
	block["blue"] = int(avg_rgb[2])

print(blocks[0])

with open("processed_blocks.json", "w") as processed_blocks_json:
	json.dump(blocks, processed_blocks_json)
