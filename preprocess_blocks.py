import json

def filter_criteria(block):
	return (not block["transparency"]) and (not block["falling"]) and (block["survival"])

with open("processed_blocks.json", "r") as blocks_json:
	blocks = json.load(blocks_json)

filtered_blocks = list(filter(filter_criteria, blocks))

with open("valid_blocks.json", "w") as blocks_json:
	json.dump(filtered_blocks, blocks_json)


