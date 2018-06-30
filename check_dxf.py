#! /usr/bin/env python
import ezdxf
import math
import argparse

parser = argparse.ArgumentParser(description='Print DXF info.')
parser.add_argument("-m", "--module", help="Enter module number", default="./")
args = parser.parse_args()

board = "GE21_M" + args.module

block_label = "BLOCK173"
if (board=="GE21_M1"): 
    # block_label = "BLOCK385"
    block_label = "BLOCK638" # chimney drawing
elif (board=="GE21_M2"):
    block_label = "BLOCK1654"
elif (board=="GE21_M3"):
    block_label = "BLOCK1743"
elif (board=="GE21_M4"):
    block_label = "BLOCK80"
elif (board=="GE21_M5"):
    block_label = "BLOCK472"
elif (board=="GE21_M6"):
    block_label = "BLOCK1220"
elif (board=="GE21_M7"):
    block_label = "BLOCK1483"
elif (board=="GE21_M8"):
    block_label = "BLOCK258"

active_area_color = 150 # blue, 50 - yellow, 82 - green, 222 - purple, 10 - red, 40 - orange
chamber_cover_color = 1
segmentation_color = 3

original_dwg = ezdxf.readfile("in/"+board+"_outline.dxf")
dwg = ezdxf.new(dxfversion=original_dwg.dxfversion)
print original_dwg.dxfversion
msp = dwg.modelspace()
dwg.layers.new(name='Strip gaps', dxfattribs={'linetype': 'Continuous', 'color': 40})
dwg.layers.new(name='Strips', dxfattribs={'linetype': 'DASHED', 'color': 222})
dwg.layers.new(name='Vias', dxfattribs={'linetype': 'Continuous', 'color': 10})

# check available linetypes
print('available line types:')
for linetype in dwg.linetypes:
    print('{}: {}'.format(linetype.dxf.name, linetype.dxf.description))

# declaring linetypes that are not default, but were used in the original
# if not present, AutoCAD would not open the file...
my_line_types = [
    ("DASHSPACE", "Dashspace - - - - - - - - - - - - - - - -", [10.0, 5.0, -5.0]),
    ("DOT", "Dot . . . . . . . . . . . . . . . . . . . ", [5.0, 0.0, -5.0]),
]
for name, desc, pattern in my_line_types:
    if name not in dwg.linetypes:
        dwg.linetypes.new(name=name, dxfattribs={'description': desc, 'pattern': pattern})

# copy board from the original DXF and paste it into the new one
importer = ezdxf.Importer(original_dwg, dwg)
importer.import_blocks(query=block_label, conflict='discard')
msp.add_blockref(block_label,(0,0), dxfattribs={
        'xscale': 1.,
        'yscale': 1.,
        'rotation': -90.
    })

# print some info for debug
block = dwg.blocks.get(block_label)  # get all INSERT entities with entity.dxf.name == "Part12"
print block.name
for e in block:
    if e.dxftype()=='LINE':
        print e.dxf.color, e.dxf.linetype, e.dxftype(), e.dxf.start, e.dxf.end

dwg.saveas("out/"+board+".dxf")
print "  open out/"+board+".dxf"
