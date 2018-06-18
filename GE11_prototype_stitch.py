#! /usr/bin/env python
import ezdxf
import math
from geo_prototype import drawSlot

dwg = ezdxf.new(dxfversion="AC1027")
msp = dwg.modelspace()

dwg.layers.new(name='Strip gaps', dxfattribs={'linetype': 'Continuous', 'color': 150})
dwg.layers.new(name='Traces', dxfattribs={'linetype': 'Continuous', 'color': 40})
dwg.layers.new(name='Strips', dxfattribs={'linetype': 'DASHED', 'color': 222})
dwg.layers.new(name='Vias', dxfattribs={'linetype': 'Continuous', 'color': 10})

# declaring linetypes that are not default, but were used in the original
# if not present, AutoCAD would not open the file...
my_line_types = [
    ("DASHSPACE", "Dashspace - - - - - - - - - - - - - - - -", [10.0, 5.0, -5.0]),
    ("DOT", "Dot . . . . . . . . . . . . . . . . . . . ", [5.0, 0.0, -5.0]),
]

# copy board from the original DXF and paste it into the new one
via_file = open("via_coord/prototype_via_centers.js",'w')
via_file.write('function CreateViaArray() {\n');
via_centers = []
for slot in range(1,13):
    via_file.write('// slot '+str(slot)+'\n');
    filename = drawSlot(slot)
    board = "GE21_M1"
    if slot<5: board = "GE21_M4"
    block_name = 'SLOT'+str(slot)
    original_dwg = ezdxf.readfile(filename)
    importer = ezdxf.Importer(original_dwg, dwg)
    importer.import_blocks(query=block_name, conflict='discard')
    x, y, angle = 0, 0, 0
    if slot<5: 
        x = -965
        y = 52
    if (slot>10):
        x = 1360
        y = -1420
        angle = 90
    if slot==7 or slot==10: y -=2
    elif slot==5 or slot==8: y +=2
    elif slot==12: x -= 2
    msp.add_blockref(block_name,(x,y), dxfattribs={
            'xscale': 1.,
            'yscale': 1.,
            'rotation': angle
        })

    via_container = dwg.blocks.get(block_name)
    for via in via_container.query('CIRCLE[layer=="Vias"]'):
        _x = via.dxf.center[0]
        _y = via.dxf.center[1]
        via_x = _x*math.cos(angle*math.pi/180)-_y*math.sin(angle*math.pi/180) + x
        via_y = _y*math.cos(angle*math.pi/180)+_x*math.sin(angle*math.pi/180) + y
        via_file.write("   x.push({:.10}); y.push({:.10});\n".format(round(via_x,4), round(via_y,4)))
        via_centers.append([via_x, via_y])

via_file.write('}\n');
via_file.close()

# adding connectors
original_dwg = ezdxf.readfile("in/GE11_skeleton.dxf")
importer = ezdxf.Importer(original_dwg, dwg)
importer.import_blocks(query='CONNECTORS', conflict='discard')
x, y = 2372,268
angle = 180
msp.add_blockref('CONNECTORS',(x,y), dxfattribs={
        'xscale': 1.,
        'yscale': 1.,
        'rotation': angle
    })
# board outline
importer.import_blocks(query='OUTLINE', conflict='discard')
msp.add_blockref('OUTLINE',(2372,268), dxfattribs={
        'xscale': 1.,
        'yscale': 1.,
        'rotation': 180
    })

# printing connector coordinates
# conn_container = dwg.blocks.get('CONNECTORS')
# for conn in conn_container.query('CIRCLE'):
#     _x = conn.dxf.center[0]
#     _y = conn.dxf.center[1]
#     conn_x = _x*math.cos(angle*math.pi/180)-_y*math.sin(angle*math.pi/180) + x
#     conn_y = _y*math.cos(angle*math.pi/180)+_x*math.sin(angle*math.pi/180) + y
#     print '[{:.10}, {:.10}]'.format(round(conn_x,4), round(conn_y,4))

conn_coord = [
    [2107.5328, 186.2558],
    [2107.4928, -95.1562],
    [2000.9792, 176.9338],
    [2000.9392, -85.8342],
    [1753.6628, 155.296],
    [1753.6228, 45.5498],
    [1753.6228, -64.1964],
    [1538.5228, 136.474],
    [1451.2928, 45.5498],
    [1538.4828, 45.5498],
    [1538.4818, -45.3744],
    [1315.8538, 45.5498],
    [1213.2928, 45.5498]
]

trc_width = 0.2


for iconn in range(len(conn_coord)):
    if (iconn<2 or iconn==8 or iconn>10): sgn_x = 1
    else: sgn_x = -1
    sgn_y = 1
    sgn_x_last, sgn_y_last = sgn_x, sgn_y

    segm1_init, segm2_init = 1, 1
    segm1, segm2 = segm1_init, segm2_init

    if (sgn_x>0): 
        pin_x, pin_y = conn_coord[iconn][0]-0.625-0.125, conn_coord[iconn][1]+1
    else:
        pin_x, pin_y = conn_coord[iconn][0]-33.5+0.625+0.125, conn_coord[iconn][1]+1

    for j in range(128):
        if (j==64):
            pin_x += sgn_x*(33.5-0.625-0.125-0.25)
            pin_y -= 4.25

        if (j>63): sgn_y = -1

        pin_x = pin_x - sgn_x*0.5
        _trc = []
        if (iconn<11):
            if (j==0 or j==64): 
                segm1, segm2 = segm1_init, segm2_init
            else:
                segm1 = segm1 + 0.7*math.sin(22.5*math.pi/180) 
                segm2 = segm2 + 0.7*math.sin(22.5*math.pi/180) 

            _trc.append((pin_x, pin_y, trc_width, trc_width))
            # segment coming out of pin
            _x = pin_x
            _y = pin_y+sgn_y*segm1
            _trc.append((_x, _y, trc_width, trc_width))
            # segment making the the turn
            no_turn = False
            no_turn = no_turn or (iconn==0 and j>63) 
            no_turn = no_turn or (iconn==1 and j<64)
            no_turn = no_turn or (iconn==2 and j>63)
            no_turn = no_turn or (iconn==3 and j<64)
            no_turn = no_turn or (iconn==6 and j<64)
            no_turn = no_turn or (iconn==8 and ((j>40 and j<64) or j>96))
            if not no_turn:
                _x = _x+sgn_x*segm1+sgn_x*math.cos(45*math.pi/180)*segm2
                _y = _y+sgn_y*math.sin(45*math.pi/180)*segm2
                _trc.append((_x, _y, trc_width, trc_width))
            # segment making it to the via
            if (iconn==2 or iconn==7):
                if (j<64):
                    if (j%2==1): 
                        idx = iconn*128+j/2+32
                        if (j==63):
                            __x = via_centers[iconn*128+(j-1)/2+96][0]
                            __y = via_centers[iconn*128+(j-1)/2+96][1]+ (via_centers[iconn*128+(j-1)/2+96][1]-via_centers[iconn*128+(j-2)/2+96][1])/2
                            _trc.append((__x, __y, trc_width, trc_width))
                        else:
                            __x = (via_centers[iconn*128+(j+1)/2+96][0] + via_centers[iconn*128+(j-1)/2+96][0])/2
                            __y = (via_centers[iconn*128+(j+1)/2+96][1] + via_centers[iconn*128+(j-1)/2+96][1])/2
                            _trc.append((__x, __y, trc_width, trc_width))
                    else: 
                        idx = iconn*128+j/2+96
                else:
                    if (j%2==1): 
                        idx = (iconn+1)*128-j/2-1
                    else: 
                        idx = (iconn+1)*128-j/2-1-64
                        __x = (via_centers[(iconn+1)*128-(j+1)/2-1][0] + via_centers[(iconn+1)*128-(j-1)/2-1][0])/2
                        __y = (via_centers[(iconn+1)*128-(j+1)/2-1][1] + via_centers[(iconn+1)*128-(j-1)/2-1][1])/2
                        _trc.append((__x, __y, trc_width, trc_width))
                _x = via_centers[idx][0]
                _y = via_centers[idx][1]
            else:
                if (iconn==4 or iconn==5 or iconn==6 or iconn==8 or iconn==9):
                    if (j<64): 
                        idx = iconn*128+64+j
                        if (iconn==8 and j%2==1) or (iconn!=8 and j%2==0):
                            _x = (via_centers[idx-1][0]+via_centers[idx+1][0])/2
                            _y = (via_centers[idx-1][1]+via_centers[idx+1][1])/2   
                            if (j==63):
                                _x = via_centers[idx-1][0]
                                _y = via_centers[idx-1][1]+ (via_centers[idx-1][1]-via_centers[idx-3][1])/2
                        else:
                            _x = via_centers[idx][0]
                            _y = via_centers[idx][1] 
                    else: 
                        idx = (iconn+1)*128-(j+1)
                        if (iconn==8 and j%2==0) or (iconn!=8 and j%2==1):
                            _x = (via_centers[idx-1][0]+via_centers[idx+1][0])/2
                            _y = (via_centers[idx-1][1]+via_centers[idx+1][1])/2   
                            if (j==127):                                                
                                _x = via_centers[idx+1][0]
                                _y = via_centers[idx+1][1]-0.65
                        else:
                            _x = via_centers[idx][0]
                            _y = via_centers[idx][1]                     
                    _trc.append((_x, _y, trc_width, trc_width))

                if (j<64):
                    _x = via_centers[iconn*128+64+j][0]
                    _y = via_centers[iconn*128+64+j][1]
                else:
                    _x = via_centers[(iconn+1)*128-(j+1)][0]
                    _y = via_centers[(iconn+1)*128-(j+1)][1]
            _trc.append((_x, _y, trc_width, trc_width))
        elif (iconn==11):
            if (j==0 or j==64): 
                segm1 = segm1_init
            elif j<50 or (j>63 and j<113):
                segm1 = segm1 + 0.5*math.sin(22.5*math.pi/180) 
            else:
                segm1 = segm1 - 0.5*math.sin(22.5*math.pi/180) 

            _trc.append((pin_x, pin_y, trc_width, trc_width))
            # segment coming out of pin
            _x = pin_x
            _y = pin_y+sgn_y*segm1
            _trc.append((_x, _y, trc_width, trc_width))
            # # segment making the the turn
            # _x = _x+sgn_x*segm1+sgn_x*math.cos(45*math.pi/180)*segm2
            # _y = _y+sgn_y*math.sin(45*math.pi/180)*segm2
            # _trc.append((_x, _y, trc_width, trc_width))
            # segment making it to the via
            if (j<64):
                _x = via_centers[iconn*128+j*2][0]
                _y = via_centers[iconn*128+j*2][1]
                if j<20:
                    _trc.append((_x-0.5, _y-0.5, trc_width, trc_width))
            else:
                _x = via_centers[iconn*128+(j-64)*2+1][0]
                _y = via_centers[iconn*128+(j-64)*2+1][1]
                if j<84:
                    _trc.append((_x-0.5, _y+0.5, trc_width, trc_width))
            _trc.append((_x, _y, trc_width, trc_width))
        elif (iconn==12):
            if (j==0 or j==64): 
                segm1 = segm1_init
            else:
                segm1 = segm1 + 0.7*math.sin(22.5*math.pi/180) 
            _trc.append((pin_x, pin_y, trc_width, trc_width))
            # segment coming out of pin
            _x = pin_x
            _y = pin_y+sgn_y*segm1
            _trc.append((_x, _y, trc_width, trc_width))
            # segment making it to the via
            if (j<64):
                _x = via_centers[iconn*128+64+j][0]
                _y = via_centers[iconn*128+64+j][1]
                _trc.append((_x-0.5, _y-0.5, trc_width, trc_width))
            else:
                _x = via_centers[(iconn)*128+j-64][0]
                _y = via_centers[(iconn)*128+j-64][1]
                _trc.append((_x-0.5, _y+0.5, trc_width, trc_width))
            _trc.append((_x, _y, trc_width, trc_width))

        msp.add_lwpolyline(_trc, dxfattribs={'layer': 'Traces'})   

board = "out/prototype.dxf"
dwg.saveas(board)
print " open",board
