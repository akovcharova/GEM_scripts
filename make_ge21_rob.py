#! /usr/bin/env python
import ezdxf
import math
import argparse, sys

#--------------------------------------------------------------
#             Some helpful geometry functions
#--------------------------------------------------------------
# intersection of a circle (x-a)^2+(y-b)^2 = R^2 and a line y = cx+d
def getLineCircleIntercept(a, b, R, c, d):
    _sqrt = math.sqrt(-a*a*c*c + 2*a*b*c - 2*a*c*d - b*b + 2*b*d + c*c*R*R - d*d + R*R)
    x0 = (-_sqrt + a + b*c - c*d)/(c*c + 1)
    y0 = c*x0 + d
    x1 = (_sqrt + a + b*c - c*d)/(c*c + 1)
    y1 = c*x1 + d
    return x0, y0, x1, y1

# intersection of line (y=ax+b) and (y=cx+d) 
def getLineLineIntercept(a, b, c, d):
    x0 = (d - b)/(a - c)
    y0 = (a*d - b*c)/(a - c)
    return x0, y0

# line definition based on two points
def getLineDef(x0, y0, x1, y1):
    a = (y0 - y1)/(x0 - x1) 
    b = (x0*y1 - x1*y0)/(x0 - x1)
    return a, b

sign = lambda x: x and (1, -1)[x < 0]

#--------------------------------------------------------------

parser = argparse.ArgumentParser(description='Print DXF info.')
parser.add_argument("-m", "--module", help="Enter module number", default="1")
parser.add_argument("-d", "--debug", help="Debug mode", action="store_true")
args = parser.parse_args()

debug = args.debug

board = "GE21_M" + args.module
nStr = 64 # number of strips connected to one side of a connector
gap = 0.2
via_radius = 0.3
trc_width = 0.15 # trace width on connector side of ROB
conn_dy = 50 


# board definition
block_label = ""
chimney_label = ""
segm_def = []
conn_list = []
opto_pts = []
opto_y0 = 0
if (board=="GE21_M1"):
    # name of block reference in input drawings for the active area and the chimney
    # this has to be retrieved by opening the input DXF files and looking up the names of the blocks
    block_label = "BLOCK385"
    chimney_label = "BLOCK336"
    # specify corners of active area
    # again, retrieve from input DXF file
    segm_def = [
      [1365.5, 244.462221+gap],
      [1756.5, 314.462022+gap]
    ]
    # specify connector positions
    conn_list.append([1505, -125, 90])
    conn_list.append([1425, -117, 90])
    conn_list.append([1425, -40, 90])
    conn_list.append([1425, 40, 90])
    conn_list.append([1425, 117, 90])
    conn_list.append([1520, 132, 90])

    conn_list.append([1615, -128, -90])
    conn_list.append([1695, -154, -90])
    conn_list.append([1695, -52, -90])
    conn_list.append([1695, 15, -90])
    conn_list.append([1695, 154, -90])
    conn_list.append([1605, 140, -90])

    # specify points defining boundary of optohybrid + space for master slave cable
    # relative to the insertion point (i.e. coordinates are local to the opto)
    opto_pts = [[-85,95], [185,95], [185,40], 
                [85,40], [85,-95], [-85,-95], [-85,95]]
    # insertion point for optohybrid, x is taken to be the middle of the board, specify Y here:
    opto_y0 = 6
elif (board=="GE21_M2"):
    block_label = "BLOCK1654"
    chimney_label = "BLOCK415"
    segm_def = [
      [1792.0, 320.817502+gap],
      [2183.0, 390.817303+gap]
    ]
    conn_list.append([1935, -180, 90])
    conn_list.append([1853, -160, 90])
    conn_list.append([1853, -55, 90])
    conn_list.append([1853, 15, 90])
    conn_list.append([1853, 160, 90])
    conn_list.append([1946, 180, 90])

    conn_list.append([2038, -190, -90])
    conn_list.append([2121, -190, -90])
    conn_list.append([2121, -60, -90])
    conn_list.append([2121, 60, -90])
    conn_list.append([2121, 190, -90])
    conn_list.append([2032, 203, -90])

    opto_pts = [[-185,95], [85,95], [85,-95], 
                [-85,-95], [-85,40], [-185, 40], [-185,95]]
    # must be the same for the master and the slave!
    opto_y0 = 6
elif (board=="GE21_M3"):
    block_label = "BLOCK1743"
    chimney_label = "BLOCK496"
    segm_def = [
      [2218.5, 397.17+gap],
      [2690.5, 481.67+gap]
    ]

    conn_list.append([2395, -248, 90])
    conn_list.append([2300, -210, 90])
    conn_list.append([2300, -65, 90])
    conn_list.append([2300, 65, 90])
    conn_list.append([2300, 210, 90])
    conn_list.append([2395, 249, 90])

    conn_list.append([2515, -260, -90])
    conn_list.append([2605, -235, -90])
    conn_list.append([2605, -75, -90])
    conn_list.append([2605, 105, -90])
    conn_list.append([2605, 235, -90])
    conn_list.append([2515, 275, -90])

    # specify points defining boundary of optohybrid + space for master slave cable
    # relative to the insertion point (i.e. coordinates are local to the opto)
    opto_pts = [[-85,95], [185,95], [185,40], 
                [85,40], [85,-95], [-85,-95], [-85,95]]
    # insertion point for optohybrid, x is taken to be the middle of the board, specify Y here:
    opto_y0 = -21
elif (board=="GE21_M4"):
    block_label = "BLOCK80"
    chimney_label = "BLOCK582"
    segm_def = [
      [2726.0, 488.029303+gap],
      [3198.0, 572.530342+gap]
    ]

    conn_list.append([2887, -320, 90])
    conn_list.append([2810, -252, 90])
    conn_list.append([2810, -85, 90])
    conn_list.append([2810, 105, 90])
    conn_list.append([2810, 252, 90])
    conn_list.append([2887, 320, 90])

    conn_list.append([3035, -352, -90])
    conn_list.append([3110, -280, -90])
    conn_list.append([3110, -95, -90])
    conn_list.append([3110, 95, -90])
    conn_list.append([3110, 280, -90])
    conn_list.append([3035, 352, -90])

    opto_pts = [[-185,95], [85,95], [85,-95], 
                [-85,-95], [-85,40], [-185, 40], [-185,95]]
    # must be the same for the master and the slave!
    opto_y0 = -21
    
elif (board=="GE21_M5"):
    block_label = "BLOCK472"
    chimney_label = "BLOCK662"
    segm_def = [
      [1365.5, 244.4622+gap],
      [1797, 321.7126+gap]
    ]

    # specify connector positions
    conn_list.append([1522, -125, 90])
    conn_list.append([1429, -117, 90])
    conn_list.append([1429, -40, 90])
    conn_list.append([1429, 40, 90])
    conn_list.append([1429, 117, 90])
    conn_list.append([1522, 132, 90])

    conn_list.append([1635, -128, -90])
    conn_list.append([1732, -154, -90])
    conn_list.append([1732, -52, -90])
    conn_list.append([1732, 15, -90])
    conn_list.append([1732, 154, -90])
    conn_list.append([1625, 140, -90])

    # specify points defining boundary of optohybrid + space for master slave cable
    # relative to the insertion point (i.e. coordinates are local to the opto)
    opto_pts = [[-85,95], [185,95], [185,40], 
                [85,40], [85,-95], [-85,-95], [-85,95]]

    opto_y0 = 6
    
elif (board=="GE21_M6"):
    block_label = "BLOCK1220"
    chimney_label = "BLOCK741"
    segm_def = [
      [0, 0+gap],
      [0, 0+gap]
    ]
elif (board=="GE21_M7"):
    block_label = "BLOCK1483"
    chimney_label = "BLOCK822"
    segm_def = [
      [0, 0+gap],
      [0, 0+gap]
    ]
elif (board=="GE21_M8"):
    block_label = "BLOCK258"
    chimney_label = "BLOCK905"
    segm_def = [
      [0, 0+gap],
      [0, 0+gap]
    ]
# split into 4 equal segments
segm_dx = (segm_def[1][0]-segm_def[0][0])/4
_a, _b = getLineDef(segm_def[0][0], segm_def[0][1], segm_def[1][0], segm_def[1][1])
segm_def.insert(1, [segm_def[0][0] + segm_dx, _a*(segm_def[0][0] + segm_dx)+_b])
segm_def.insert(2, [segm_def[0][0] + 2*segm_dx, _a*(segm_def[0][0] + 2*segm_dx)+_b])
segm_def.insert(3, [segm_def[0][0] + 3*segm_dx, _a*(segm_def[0][0] + 3*segm_dx)+_b])

nConn = len(conn_list)/2
nEta = len(segm_def)-1

# create output DXF file
dwg = ezdxf.new(dxfversion='AC1027')
msp = dwg.modelspace()
dwg.layers.new(name='Strip gaps', dxfattribs={'linetype': 'Continuous', 'color': 150})
dwg.layers.new(name='Even strips', dxfattribs={'linetype': 'DASHED', 'color': 161})
dwg.layers.new(name='Odd strips', dxfattribs={'linetype': 'DASHED', 'color': 151})
dwg.layers.new(name='Vias', dxfattribs={'linetype': 'Continuous', 'color': 1})
dwg.layers.new(name='Traces', dxfattribs={'linetype': 'Continuous', 'color': 40})

# declaring linetypes that are not default, but were used in the input
# if not present, AutoCAD would not open the file...
my_line_types = [
    ("DASHSPACE", "Dashspace - - - - - - - - - - - - - - - -", [10.0, 5.0, -5.0]),
    ("DOT", "Dot - - - - - - - - - - - - - - - -", [5.0, 5.0, -5.0])
    # ("DOT", "Dot . . . . . . . . . . . . . . . . . . . ", [5.0, 0.0, -5.0])
]
for name, desc, pattern in my_line_types:
    if name not in dwg.linetypes:
        dwg.linetypes.new(name=name, dxfattribs={'description': desc, 'pattern': pattern})

# --------------------------------------------------------------
#         Draw strip gaps
# --------------------------------------------------------------
str_line_def = []
width_lo = segm_def[0][1]*2
width_hi = segm_def[-1][1]*2

str_width_lo = (width_lo - (nStr*nConn+1)*gap)/(nStr*nConn)
str_width_hi = (width_hi - (nStr*nConn+1)*gap)/(nStr*nConn)
for i in range(nStr*nConn+1):
    # gaps
    _start = (segm_def[0][0], i*(str_width_lo+gap) + gap/2. - width_lo/2., gap, gap)
    _end = (segm_def[-1][0], i*(str_width_hi+gap) + gap/2. - width_hi/2., gap, gap)
    if not debug:
        msp.add_lwpolyline([_start, _end], dxfattribs={'layer': 'Strip gaps'})

# also the gaps between eta segments
for iseg in range(nEta+1):
    if (iseg==0):
        msp.add_lwpolyline([(segm_def[iseg][0]-gap/2,segm_def[iseg][1], gap, gap), 
            (segm_def[iseg][0]-gap/2, -segm_def[iseg][1], gap, gap)], 
            dxfattribs={'layer': 'Strip gaps'})
    elif (iseg==nEta):   
        msp.add_lwpolyline([(segm_def[iseg][0]+gap/2,segm_def[iseg][1], gap, gap), 
            (segm_def[iseg][0]+gap/2, -segm_def[iseg][1], gap, gap)], 
            dxfattribs={'layer': 'Strip gaps'})
    else:
        msp.add_lwpolyline([(segm_def[iseg][0],segm_def[iseg][1], gap, gap), 
            (segm_def[iseg][0], -segm_def[iseg][1], gap, gap)], 
            dxfattribs={'layer': 'Strip gaps'})

# --------------------------------------------------------------
#         Save location of center of each strip - 
#         used to determine the vias placement
# --------------------------------------------------------------

for i in range(nStr*nConn):
    strip_layer = "Odd strips"
    if ((i/nStr)%2==0): strip_layer = "Even strips"
    str_lo_x = segm_def[0][0]
    str_lo_y = i*(str_width_lo+gap) + gap + str_width_lo/2. - width_lo/2.
    str_hi_x = segm_def[-1][0]
    str_hi_y = i*(str_width_hi+gap) + gap + str_width_hi/2. - width_hi/2.
    _a,_b = getLineDef(str_lo_x, str_lo_y, str_hi_x, str_hi_y)
    str_line_def.append([_a, _b])
    if (debug and not (i/nStr)%2==0): 
        msp.add_lwpolyline([(segm_def[0][0], _a*segm_def[0][0]+_b),
            (segm_def[-1][0], _a*segm_def[-1][0]+_b)], 
            dxfattribs={'layer': strip_layer})

# --------------------------------------------------------------
#   Place connectors, routing and some simple
#   rectangles to designate VFAT, OPTO and needed clearance
# --------------------------------------------------------------

# import connector footprint
conn_name = 'Hirose'
conn_dwg = ezdxf.readfile("in/HIROSE_FX10A_140S_14_SV.dxf")
conn_importer = ezdxf.Importer(conn_dwg, dwg)
conn_importer.import_blocks(query=conn_name, conflict='discard')

# draw rectangles around the connectors denoting the VFAT+Flex and a 5mm buffer zone
vfat = dwg.blocks.new(name='VFAT')
vfat.add_lwpolyline([(26,-6.5, trc_width, trc_width),
                    (26,66.5, trc_width, trc_width),
                    (-26,66.5, trc_width, trc_width),
                    (-26,-6.5, trc_width, trc_width),
                    (26,-6.5, trc_width, trc_width)])

_buff = 5
vfat.add_lwpolyline([(26+_buff,-6.5-_buff, trc_width, trc_width),
                    (26+_buff,66.5+_buff, trc_width, trc_width),
                    (-26-_buff,66.5+_buff, trc_width, trc_width),
                    (-26-_buff,-6.5-_buff, trc_width, trc_width),
                    (26+_buff,-6.5-_buff, trc_width, trc_width)])

opto = dwg.blocks.new(name='OPTO')
opto.add_lwpolyline([(i[0],i[1], trc_width, trc_width) for i in opto_pts])

msp.add_blockref("OPTO",((segm_def[0][0]+segm_def[-1][0])/2, opto_y0), dxfattribs={
    'xscale': 1.,
    'yscale': 1.,
    'rotation': 0
    })

via_centers = [] # [None] * (2*nStr*nConn)
for i,iconn in enumerate(conn_list):
    # draw connectors, just to see if all looks good
    msp.add_blockref(conn_name,(iconn[0],iconn[1]), dxfattribs={
            'xscale': 1.,
            'yscale': 1.,
            'rotation': iconn[2]
        })
    msp.add_blockref("VFAT",(iconn[0],iconn[1]), dxfattribs={
        'xscale': 1.,
        'yscale': 1.,
        'rotation': iconn[2]
        })

    ii = i%nConn # which number is it in this row

    # determine order in which the traces will be laid out
    # depending on the relative position of the connector to it's set of strips
    sgn_trc_y, sgn_pin_dy = 1,1 
    ordered_strips = []
    imidstr = ii*nStr+nStr/2-1
    midstr_y = str_line_def[imidstr][0]*iconn[0]+ str_line_def[imidstr][1]
    if iconn[1]-midstr_y>0:
        sgn_trc_y = -1 # traces will bend down
        sgn_pin_dy = 1 # starting at the pin with lowest Y coord and moving up
        ordered_strips = range(0, 64) # starting at the trace with lowest Y coord
    else:
        sgn_trc_y = 1
        sgn_pin_dy = -1
        ordered_strips = range(63, -1, -1)

    first_str_y = str_line_def[ii*nStr][0]*iconn[0]+ str_line_def[ii*nStr][1]
    last_str_y = str_line_def[(ii+1)*nStr-1][0]*iconn[0]+ str_line_def[(ii+1)*nStr-1][1]
    

    # there are nStr strips on each of the two sides of the connector
    turn_measure = 0.5*math.sin(22.5*math.pi/180)
    for iside in [0,1]: 
        # initialize segment length for trace coming out of the lowest pin of each connector
        dl1, dl2 , dl3 = 3, 1, 64*2*turn_measure-5
        if i in [0,5,6,11]: dl1 = 1
        # dlen controls if the segment length coming out of each pin (dl1) is decreasing or increasing
        dlen = 1

        # variable that controls how far to place the row of vias
        min_dx_vias_conn = 30

        # variable that holds the Y coordinate of the current pin
        pin_dy = 0

        for j,istr in enumerate(ordered_strips):
            # if j>0: continue
            # determine X coordinate of pin
            if iside==0: sgn_x = -1
            else: sgn_x = 1
            pin_x = iconn[0] + sgn_x*3 

            # determine Y coordinate of pin
            if (j==0): pin_dy = 0
            elif ((j-2)%10==0 and j<nStr): pin_dy += 1.5
            else: pin_dy += 0.5
            pin_y = iconn[1] - sgn_pin_dy*(19.25 - pin_dy)

            # determine via locations
            dx_half = segm_def[i/nConn*2+1][0]-(iconn[0]+sgn_x*5)
            if (dx_half*sgn_x>0):
                via_x = segm_def[i/nConn*2+1][0] + sgn_x*2
            else:
                via_x = iconn[0] + sgn_x*min_dx_vias_conn
            via_y = str_line_def[ii*nStr+istr][0]*via_x + str_line_def[ii*nStr+istr][1]

            if (pin_y-via_y)*sgn_trc_y>0: dlen =-1

            _trc = []
            _x, _y = pin_x, pin_y
            _trc.append((_x, _y, trc_width, trc_width))
            if i in [0,5,6,11]:
                dl1 += 1.2*turn_measure 
                # segment coming out of pin
                _x = pin_x+sgn_x*dl1 
                _trc.append((_x, _y, trc_width, trc_width))
                # turning segment
                sgn_y = 1
                if (via_y<_y): sgn_y = -1 
                dl2 += 1.4*turn_measure 
                _x += sgn_x*dl2
                _y += sgn_y*dl2
                
                _trc.append((_x, _y, trc_width, trc_width))
                # treat separately traces that can go straight to the via vs those that need one more turn
                if iconn[2]*sgn_x>0:
                    # find strip Y coordinate at this _x
                    _idx = ii*nStr+istr
                    _y = str_line_def[_idx][0]*_x + str_line_def[_idx][1]
                    _trc.append((_x, _y-sgn_y*0.5, trc_width, trc_width))
                    # make a small turn along the strip right before the via, 
                    # otherwise vias may be too close to the next strip
                    _x = _x+sgn_x*0.5
                    _y = str_line_def[_idx][0]*_x + str_line_def[_idx][1]
                    _trc.append((_x, _y, trc_width, trc_width))
                    # move the via to this point since we have already arrived at the strip
                    via_x, via_y = _x, _y
                else:
                    # first turn toward vias ...
                    _idx = ii*nStr+ordered_strips[-1]
                    _y = str_line_def[_idx][0]*_x + str_line_def[_idx][1]
                    _y += sgn_trc_y*dl3
                    dl3 -= 2*turn_measure
                    _trc.append((_x, _y, trc_width, trc_width))
                    # second turn ...
                    _x = segm_def[i/nConn*2+1][0] - sgn_x*2.5
                    _idx = ii*nStr+istr
                    _y = str_line_def[_idx][0]*_x + str_line_def[_idx][1]
                    _trc.append((_x, _y, trc_width, trc_width))
                    # go to via
                    _trc.append((via_x, via_y, trc_width, trc_width))
            else:
                dl1 += 1.3*dlen*turn_measure 
                # segment coming out of pin
                _x = pin_x+sgn_x*dl1 
                _trc.append((_x, _y, trc_width, trc_width))
                # make a small turn along the strip right before the via, 
                # otherwise vias may be too close to the next strip
                _idx = ii*nStr+istr
                _x = via_x-sgn_x*0.5
                _y = str_line_def[_idx][0]*_x + str_line_def[_idx][1]
                _trc.append((_x, _y, trc_width, trc_width))
                # segment reaching to the via
                _trc.append((via_x, via_y, trc_width, trc_width))
                
            if not debug:
                msp.add_lwpolyline(_trc, dxfattribs={'layer': 'Traces'})
                msp.add_circle((via_x, via_y), via_radius, dxfattribs={'layer': 'Vias'})
                via_centers.append([via_x, via_y])
            
# --------------------------------------------------------------
#   Import drawings of board outline, active area and chimney
# --------------------------------------------------------------

outline_dwg = ezdxf.readfile("in/"+board+"_outline.dxf")
outline_importer = ezdxf.Importer(outline_dwg, dwg)
outline_importer.import_blocks(query=block_label, conflict='discard')
board_rotation = -90.   
msp.add_blockref(block_label,(0,0), dxfattribs={
        'xscale': 1.,
        'yscale': 1.,
        'rotation': board_rotation
    })

chimney_dwg = ezdxf.readfile("in/"+board+"_chimney.dxf")
outline_importer = ezdxf.Importer(chimney_dwg, dwg)
outline_importer.import_blocks(query=chimney_label, conflict='discard')
board_rotation = -90.
msp.add_blockref(chimney_label,(0,0), dxfattribs={
        'xscale': 1.,
        'yscale': 1.,
        'rotation': board_rotation
    })

#------------------------------------------------
#         Save via locations to a text file
#------------------------------------------------
js_file = open('via_coord/'+board+'_coord.js','w')
js_file.write('function CreateConnectorArray_'+board+'() {\n');
for iconn in conn_list:
    js_file.write("\tconn_x.push({:.10});".format(round(iconn[0],4)))
    js_file.write("\tconn_y.push({:.10});".format(round(iconn[1],4)))
    js_file.write("\tconn_ang.push({:.10});\n".format(round(iconn[2],0)))
js_file.write('}\n\n');
js_file.write('function CreateViaArray_'+board+'() {\n');
for ivia in via_centers:
    js_file.write("\tx.push({:.10});".format(round(ivia[0],4)))
    js_file.write("\ty.push({:.10});\n".format(round(ivia[1],4)))
js_file.write('}\n');
js_file.close()

#------------------------------------------------
#        Save output drawing to a DXF file
#------------------------------------------------
fname = "out/"+board+".dxf"
if (debug): fname = "out/"+board+"_dbg.dxf"
dwg.saveas(fname)
print "open "+fname

