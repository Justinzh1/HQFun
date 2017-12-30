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
gs = g.GSearch()
while True:
    command = raw_input(">")
    if command == '':
        filename = process.screenshot()
        line_and_word_boxes = tool.image_to_string(
            Image.open(filename), lang="eng",
            builder=pyocr.builders.LineBoxBuilder()
        )
        question, choices = process.parse_input(line_and_word_boxes)
        count = gs.threaded_query(question, choices, 15)
        id += 1
