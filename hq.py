from PIL import Image
import sys

import pyocr
import pyocr.builders
import pdb

import process
import gsearch as g

tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
# The tools are returned in the recommended order of usage
tool = tools[0]

# list of box objects. For each box object:
#   box.content is the word in the box
#   box.position is its position on the page (in pixels)
#
# Beware that some OCR tools (Tesseract for instance)
# may return empty boxes

id = 0 # TODO organize saving screenshots better


while True:
	command = raw_input("::")
	if command == 's':
		filename = process.screenshot()
		try:
			line_and_word_boxes = tool.image_to_string(
				Image.open(filename), lang="eng",
				builder=pyocr.builders.LineBoxBuilder()
			)
			# pdb.set_trace()
			question, choices = process.parse_input(line_and_word_boxes)
			count = gsearch.query(question, choices, 7)
			print(count)
		except:
			continue
		id += 1