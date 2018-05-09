#! /usr/bin/env python
import ezdxf
import math

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

debug = False
draw_gaps = False
draw_via_rows = False
OH4 = True

board = "GE21_M1"

block_label = "BLOCK173"
chimney_label = ""
if (board=="GE21_M1"): 
    block_label = "BLOCK385"
    chimney_label = "BLOCK638"
elif (board=="GE21_M4"): 
    block_label = "BLOCK80"
    chimney_label = "BLOCK432"


# handles for finding lines on the drawing
active_area_color = 150 # blue, 50 - yellow, 82 - green, 222 - purple, 10 - red, 40 - orange
chamber_cover_color = 1
segmentation_color = 3

# nEtaSegm = 8
# nStripsPerConn = 12 #128
# nConnPerRow = 3
# gap = 2 #0.2
# via_radius = 3.5 #0.3

nEtaSegm = 8
nConnectors = 24
nConnPerRow = 3
nStripsPerConn = 128
gap = 0.2
via_radius = 0.3
if (board!="ME0"):
    nEtaSegm = 2
    nConnectors = 12
    nConnPerRow = 6

# define segment by the highest point in Y
segm_def = []
if (board=="ME0"):
    segm_def = [
      [660.0, 117.588162+gap],
      [727.456, 129.616053+gap],
      [801.892, 142.888528+gap],
      [884.139, 157.553761+gap],
      [975.077, 173.768662+gap],
      [1075.708, 191.711895+gap],
      [1187.178, 211.587799+gap],
      [1310.804, 230.0+gap],
      [1448.0, 230.0+gap]
    ]
elif (board=="GE21_M1"):
    segm_def = [
      [1365.5, 244.462221+gap],
      [1561.0, 279.4608+gap],
      [1756.5, 314.462022+gap]
    ]
elif (board=="GE21_M4"):
    segm_def = [
      [2726.0, 488.029303+gap],
      [2962.0, 530.28+gap],
      [3198.0, 572.530342+gap]
    ]


# ME0 is not a trapezoid so need the additional geometrical constraints 
bites = []
if (board=="ME0"):
    bites = [
        [(1448.0, -230.0-gap/2., gap, gap), (1290.439116, -230.0-gap/2., gap, gap)],
        [(1448.0, 230.0+gap/2., gap, gap), (1290.439116, 230.0+gap/2., gap, gap)]
    ]

# slope and intercept of line defining the chimney for positive X
# to retrieve coordinates run check_dxf on the chimney drawing
chimney_def_a, chimney_def_b = 0,0
if (board == "GE21_M1"):
    chimney_def_a, chimney_def_b = getLineDef(1346.5, 123.256591, 1773.5, 198.548212)

# specify where to place the vias in each segment
via_row_radii = [0]*nEtaSegm
if (board=='ME0'):
    if (nEtaSegm!=8): # for tests just put the via rows in the middle of segment
        for iseg in range(nEtaSegm):
            via_row_radii[iseg] = (segm_def[iseg+1][0] + segm_def[iseg][0])/2
    else: # adjust radii to make room for Optohybrid and connectors
        for iseg in range(3):
            via_row_radii[iseg] = segm_def[iseg+1][0]-10*via_radius
        via_row_radii[3] = segm_def[4][0]-10
        via_row_radii[4] = segm_def[5][0]-25
        via_row_radii[5] = segm_def[6][0]-50
        via_row_radii[6] = segm_def[7][0]-80
        via_row_radii[7] = segm_def[7][0] + 20 + 2*via_radius
elif (board=="GE21_M1"):
    via_row_radii = [segm_def[0][0]+110, segm_def[0][0]+260]
elif (board=="GE21_M4"):
    via_row_radii = [segm_def[0][0]+110, segm_def[0][0]+410]


if (debug):          
    for i in via_row_radii: print i

dwg = ezdxf.new(dxfversion='AC1027')
msp = dwg.modelspace()
dwg.layers.new(name='Strip gaps', dxfattribs={'linetype': 'Continuous', 'color': 40})
dwg.layers.new(name='Even strips', dxfattribs={'linetype': 'DASHED', 'color': 222})
dwg.layers.new(name='Center strips', dxfattribs={'linetype': 'DASHED', 'color': 90})
dwg.layers.new(name='Odd strips', dxfattribs={'linetype': 'DASHED', 'color': 170})
dwg.layers.new(name='Vias', dxfattribs={'linetype': 'Continuous', 'color': 90})
dwg.layers.new(name='Traces', dxfattribs={'linetype': 'Continuous', 'color': 10})

# check available linetypes
# print('available line types:')
# for linetype in dwg.linetypes:
#     print('{}: {}'.format(linetype.dxf.name, linetype.dxf.description))

# declaring linetypes that are not default, but were used in the original
# if not present, AutoCAD would not open the file...
my_line_types = [
    ("DASHSPACE", "Dashspace - - - - - - - - - - - - - - - -", [10.0, 5.0, -5.0]),
    ("DOT", "Dot . . . . . . . . . . . . . . . . . . . ", [5.0, 0.0, -5.0]),
]
for name, desc, pattern in my_line_types:
    if name not in dwg.linetypes:
        dwg.linetypes.new(name=name, dxfattribs={'description': desc, 'pattern': pattern})


# --------------------------------------------------------------
#   Import drawings of board outline, active area and chimney
# --------------------------------------------------------------

outline_dwg = ezdxf.readfile("in/"+board+"_outline.dxf")
outline_importer = ezdxf.Importer(outline_dwg, dwg)
outline_importer.import_blocks(query=block_label, conflict='discard')
board_rotation = 180.
if (board!="ME0"):
    board_rotation = -90.
msp.add_blockref(block_label,(0,0), dxfattribs={
        'xscale': 1.,
        'yscale': 1.,
        'rotation': board_rotation
    })

if (board!="ME0"):  
    chimney_dwg = ezdxf.readfile("in/"+board+"_chimney.dxf")
    outline_importer = ezdxf.Importer(chimney_dwg, dwg)
    outline_importer.import_blocks(query=chimney_label, conflict='discard')
    board_rotation = -90.
    msp.add_blockref(chimney_label,(0,0), dxfattribs={
            'xscale': 1.,
            'yscale': 1.,
            'rotation': board_rotation
        })

# --------------------------------------------------------------
#         Calculate location of strip gaps
# --------------------------------------------------------------
me0_maxy = 0
if (board == 'ME0'): # do not extrapolate strips all the way due to irregular shape
    _c,_d = getLineDef(segm_def[0][0], segm_def[0][1], segm_def[-3][0], segm_def[-3][1])
    me0_maxy = _c*segm_def[-1][0]+_d

gap_pts_lo, gap_pts_hi = [], []
gap_line_def = []
str_line_def = []
width_lo = segm_def[0][1]*2
width_hi = segm_def[-1][1]*2
if (board=='ME0'):
    width_hi = me0_maxy*2

str_width_lo = (width_lo - (nStripsPerConn*nConnPerRow+1)*gap)/(nStripsPerConn*nConnPerRow)
str_width_hi = (width_hi - (nStripsPerConn*nConnPerRow+1)*gap)/(nStripsPerConn*nConnPerRow)
for i in range(nStripsPerConn*nConnPerRow+1):
    # gaps
    gap_pts_lo.append((segm_def[0][0], i*(str_width_lo+gap) + gap/2. - width_lo/2., gap, gap))
    # high end of gaps
    if (board=='ME0'):
        _x = segm_def[-1][0]
        _y = i*(str_width_hi+gap) + gap/2 - width_hi/2.
        if (abs(_y) > segm_def[-1][1]):
            _a,_b = getLineDef(gap_pts_lo[-1][0], gap_pts_lo[-1][1], _x, _y)
            _c,_d = 0, sign(_y)*bites[-1][0][1] # bites slope is 0 and intercept is y
            _x,_y = getLineLineIntercept(_a,_b,_c,_d)
        gap_pts_hi.append((_x, _y, gap, gap))
    else:
        gap_pts_hi.append((segm_def[-1][0], i*(str_width_hi+gap) + gap/2. - width_hi/2., gap, gap))
    # also need the line definition for finding overlaps with vias later
    _a, _b = getLineDef(gap_pts_lo[-1][0], gap_pts_lo[-1][1], gap_pts_hi[-1][0], gap_pts_hi[-1][1])
    gap_line_def.append([_a,_b])


# --------------------------------------------------------------
#         Save location of center of each strip
# --------------------------------------------------------------

for i in range(nStripsPerConn*nConnPerRow):
    strip_layer = "Odd strips"
    if ((i/nStripsPerConn)%2==0): strip_layer = "Even strips"
    if ((i%nStripsPerConn)==63): strip_layer = "Center strips"
    str_lo_x = segm_def[0][0]
    str_lo_y = i*(str_width_lo+gap) + gap + str_width_lo/2. - width_lo/2.
    str_hi_x = segm_def[-1][0]
    str_hi_y = i*(str_width_hi+gap) + gap + str_width_hi/2. - width_hi/2.
    _a,_b = getLineDef(str_lo_x, str_lo_y, str_hi_x, str_hi_y)
    str_line_def.append([_a, _b])
    msp.add_lwpolyline([(segm_def[0][0], _a*segm_def[0][0]+_b),(segm_def[-1][0], _a*segm_def[-1][0]+_b)], dxfattribs={'layer': strip_layer})

#------------------------------------------------
#                Connectors 
#------------------------------------------------

# import connector footprint
conn_name = 'Hirose'
conn_dwg = ezdxf.readfile("in/HIROSE_FX10A_140S_14_SV.dxf")
conn_importer = ezdxf.Importer(conn_dwg, dwg)
conn_importer.import_blocks(query=conn_name, conflict='discard')

# place connectors
rows_x = [segm_def[0][0]+10, segm_def[-1][0]-10]
conn_dx = 50
conn_dy = 70
conn_edge_gap_x = 5
conn_edge_gap_y = 10
if (board=="GE21_M1"): 
    rows_x = [segm_def[0][0]+conn_edge_gap_x, 
              segm_def[0][0]+conn_dy+2*conn_edge_gap_x, 
              segm_def[-1][0]-2*conn_dy-2*conn_edge_gap_x, 
              segm_def[-1][0]-conn_dy-conn_edge_gap_x]

# this is the number of connectors per row of connectors, vs nConnPerRow = number of connectors per row of Strips
conn_list = []
_x = segm_def[0][0] + conn_edge_gap_x + 25 + 6.5 
_x2 = _x + conn_dy + conn_edge_gap_y
conn_list.append([_x2, -((chimney_def_a*_x2+chimney_def_b)-conn_edge_gap_y-25), -90])
conn_list.append([_x,  -((chimney_def_a*_x+chimney_def_b)-conn_edge_gap_y-25), -90])
_cstrip = 3*128+63
conn_list.append([_x,  -(str_line_def[_cstrip][0]*_x + str_line_def[_cstrip][1]), -90])
conn_list.append([_x,  str_line_def[_cstrip][0]*_x + str_line_def[_cstrip][1], -90])
conn_list.append([_x,  (chimney_def_a*_x+chimney_def_b)-conn_edge_gap_y-25, -90])
conn_list.append([_x2, (chimney_def_a*_x2+chimney_def_b)-conn_edge_gap_y-25, -90])

_x = segm_def[-1][0] - conn_edge_gap_x - 25 - 6.5 
_x2 = _x - conn_dy - conn_edge_gap_y
conn_list.append([_x2, -((chimney_def_a*(_x2-conn_dy+6.5)+chimney_def_b)-conn_edge_gap_y-25), 90])
conn_list.append([_x,  -((chimney_def_a*(_x-conn_dy+6.5)+chimney_def_b)-conn_edge_gap_y-25), 90])
_cstrip = 3*128+63
if (OH4):
    conn_list.append([_x,  -(str_line_def[_cstrip][0]*(_x-conn_dy+6.5) + str_line_def[_cstrip][1]), 90])
    conn_list.append([_x,  str_line_def[_cstrip][0]*(_x-conn_dy+6.5) + str_line_def[_cstrip][1]-30, 90])
else:
    conn_list.append([_x-120,  -(str_line_def[_cstrip][0]*(_x-conn_dy+6.5) + str_line_def[_cstrip][1]), 90])
    conn_list.append([_x-120,  str_line_def[_cstrip][0]*(_x-conn_dy+6.5) + str_line_def[_cstrip][1], 90])    
conn_list.append([_x,  (chimney_def_a*(_x-conn_dy+6.5)+chimney_def_b)-conn_edge_gap_y-25, 90])
conn_list.append([_x2, (chimney_def_a*(_x2-conn_dy+6.5)+chimney_def_b)-conn_edge_gap_y-25, 90])

trc_width = 0.15
trc_gap = 0.2
via_centers = []
for i,iconn in enumerate(conn_list):
    msp.add_blockref(conn_name,(iconn[0],iconn[1]), dxfattribs={
            'xscale': 1.,
            'yscale': 1.,
            'rotation': iconn[2]
        })
    if (i%6==0): via_centers.append([])
    # make the names sensical in case i need them later
    if (abs(iconn[2])==90):
        _conn_dx = conn_dx
        conn_dx = conn_dy
        conn_dy = _conn_dx

    segm1_init, segm2_init = 1, 1
    segm1, segm2 = segm1_init, segm2_init
    sgn_x_last, sgn_y_last = -1, 1
    sgn_x, sgn_y = sgn_x_last, sgn_y_last
    pin_dy = 0
    via_order = True
    midstr_y = str_line_def[(i%6)*128+63][0]*iconn[0]+ str_line_def[(i%6)*128+63][1]
    if (iconn[1]>0):
        closest_str_y = str_line_def[(i%6)*128][0]*iconn[0]+ str_line_def[(i%6)*128][1]
    else:
        closest_str_y = str_line_def[(i%6)*128+127][0]*iconn[0]+ str_line_def[(i%6)*128+127][1]
    for j in range(128):
        istr = j

        if (iconn[1]>0):
            istr = 127-j
            if (iconn[1]-conn_dy/2)<closest_str_y:
                sgn_y = 1
            else: 
                if (j<63):           
                    sgn_y = 1
                else:
                    sgn_y = -1
        else:
            istr = j
            if (iconn[1]+conn_dy/2)>closest_str_y:
                sgn_y = -1
            else:
                if (j<63):           
                    sgn_y = -1
                else:
                    sgn_y = 1

        if (j>63): sgn_x = 1
        else: sgn_x = -1
        pin_x = iconn[0] + sgn_x*3 

        if (istr==0 or istr==64): pin_dy = 0
        elif ((istr-2)%10==0 and istr<64): pin_dy = pin_dy + 1.5
        elif ((istr-66)%10==0 and istr>63): pin_dy = pin_dy + 1.5
        else: pin_dy = pin_dy + 0.5
        pin_y = iconn[1] + sgn_y*(19.25 - pin_dy)


        if (sgn_x*sgn_x_last<0): 
            segm1, segm2 = segm1_init, segm2_init
            sgn_x_last = sgn_x 
        else: 
            segm1 = segm1 + 0.7*math.sin(22.5*math.pi/180) 
            segm2 = segm2 + 0.7*math.sin(22.5*math.pi/180) 

        _trc = []
        _trc.append((pin_x, pin_y, trc_width, trc_width))
        # segment coming out of pin
        _trc.append((pin_x+sgn_x*segm1, pin_y, trc_width, trc_width))
        # segment making the the turn
        via_x = pin_x+sgn_x*segm1+sgn_x*math.cos(45*math.pi/180)*segm2
        _y = pin_y+sgn_y*math.sin(45*math.pi/180)*segm2
        _trc.append((via_x, _y, trc_width, trc_width))
        # segment reaching to the via
        if (istr<64):
            via1_y = str_line_def[(i%6)*128+istr][0]*via_x + str_line_def[(i%6)*128+istr][1]
            via2_y = str_line_def[(i%6)*128+63-istr][0]*via_x + str_line_def[(i%6)*128+(63-istr)][1]
            if (istr==0): via_order = abs(via1_y-pin_y)>abs(via2_y-pin_y)
        else:
            via1_y = str_line_def[(i%6)*128+istr][0]*via_x + str_line_def[(i%6)*128+istr][1]
            via2_y = str_line_def[(i%6)*128+191-istr][0]*via_x + str_line_def[(i%6)*128+(191-istr)][1]
            if (istr==64): via_order = abs(via1_y-pin_y)>abs(via2_y-pin_y)

        if via_order:
            _trc.append((via_x, via1_y, trc_width, trc_width))
            via_centers[-1].append((via_x,via1_y))
            msp.add_circle((via_x, via1_y), via_radius, dxfattribs={'layer': 'Vias'})
        else:
            _trc.append((via_x, via2_y, trc_width, trc_width))
            via_centers[-1].append((via_x,via2_y))
            msp.add_circle((via_x, via2_y), via_radius, dxfattribs={'layer': 'Vias'})
        msp.add_lwpolyline(_trc, dxfattribs={'layer': 'Strip gaps'})

# ---------------------------------------------------
#        Original connector scheme
# ---------------------------------------------------
# rows_x = [segm_def[0][0]+10, segm_def[-1][0]-10]
# conn_dx = 50
# conn_dy = 70
# conn_edge_gap_x = 0
# conn_edge_gap_y = 10
# if (board=="GE21_M1"): 
#     if (OH4):
#         rows_x = [segm_def[0][0]+conn_edge_gap_x, 
#                   segm_def[0][0]+conn_dx+20+conn_edge_gap_x, 
#                   segm_def[-1][0]-2*conn_dx-25-conn_edge_gap_x, 
#                   segm_def[-1][0]-conn_dx-conn_edge_gap_x]
#     else:
#         rows_x = [segm_def[0][0]+conn_edge_gap_x, 
#                   segm_def[0][0]+conn_dx+20+conn_edge_gap_x, 
#                   segm_def[1][0], 
#                   segm_def[1][0]+conn_dx+10]

# # this is the number of connectors per row of connectors, vs nConnPerRow = number of connectors per row of Strips
# nConnPerRow_tmp = nConnectors/len(rows_x)
# center_conn_offset = 0 
# conn_list_tmp = []
# for irow in range(len(rows_x)):
#     _y = chimney_def_a*rows_x[irow] + chimney_def_b
#     conn_gap_y = (2*_y-2*conn_edge_gap_y - nConnPerRow_tmp*conn_dy)/(nConnPerRow_tmp-1)
#     for iconn in range(nConnPerRow_tmp):
#         iconn_y = _y - conn_edge_gap_y - iconn*(conn_dy+conn_gap_y) - 6.5
#         iconn_x = rows_x[irow] + conn_dx - 25
#         conn_rotation = 180
#         if (nConnPerRow_tmp == 3):
#             if (iconn==2 or (irow%2==1 and iconn>0)):
#                 iconn_y = iconn_y - conn_dy +13
#                 iconn_x = rows_x[irow] + 25
#                 conn_rotation = 0
#             if (iconn==1):
#                 if (irow%2==0): 
#                     center_conn_offset = conn_gap_y/2
#                     # also leave room for Master - Slave cable
#                     if (irow!=2): iconn_y = iconn_y + center_conn_offset
#                 else:
#                     iconn_y = iconn_y - center_conn_offset
#         conn_list_tmp.append([iconn_x, iconn_y, conn_rotation])

# # cruch
# conn_list = [conn_list_tmp[3], conn_list_tmp[0], conn_list_tmp[1],
#              conn_list_tmp[4], conn_list_tmp[2], conn_list_tmp[5],
#              conn_list_tmp[6], conn_list_tmp[9], conn_list_tmp[7],
#              conn_list_tmp[10], conn_list_tmp[11], conn_list_tmp[8]]
# if (not OH4):
#     conn_list = [conn_list_tmp[3], conn_list_tmp[0], conn_list_tmp[1],
#              conn_list_tmp[4], conn_list_tmp[2], conn_list_tmp[5],
#              conn_list_tmp[9], conn_list_tmp[6], conn_list_tmp[7],
#              conn_list_tmp[10], conn_list_tmp[8], conn_list_tmp[11]]

# trc_width = 0.15
# trc_gap = 0.2
# via_centers = []
# nStripLines = len(str_line_def)
# for i,iconn in enumerate(conn_list):
#     msp.add_blockref(conn_name,(iconn[0],iconn[1]), dxfattribs={
#             'xscale': 1.,
#             'yscale': 1.,
#             'rotation': iconn[2]
#         })

#     if (i%6==0): via_centers.append([])


#     segm1_init, segm2_init = 1, 1
#     segm1, segm2 = segm1_init, segm2_init
#     sign_y_last, sign_x_last = -1, 1
#     sign_y, sign_x = sign_y_last, sign_x_last
#     pin_dx = 0
#     for istr in range(128):
#         if (istr<64): sign_y = 1
#         else: sign_y = -1
#         pin_y = iconn[1] + sign_y*3 

#         if (istr==0 or istr==64): pin_dx = 0
#         elif ((istr-2)%10==0 and istr<64): pin_dx = pin_dx + 1.5
#         elif ((istr-66)%10==0 and istr>63): pin_dx = pin_dx + 1.5
#         else: pin_dx = pin_dx + 0.5
#         if (iconn[1]>0): pin_x = iconn[0] + sign_x*(19.25 - pin_dx)
#         else: pin_x = iconn[0] - sign_x*(19.25 - pin_dx)

#         _trc = []
#         _trc.append((pin_x, pin_y, trc_width, trc_width))
#         via_x = pin_x
#         _istr = (nStripLines-1) - ((i%6)*128+istr)
#         via_y = str_line_def[_istr][0]*pin_x+ str_line_def[_istr][1]
#         if (istr<64 and iconn[1]>0) or (istr>63 and iconn[1]<0):
#             _trc.append((via_x, via_y, trc_width, trc_width))    
#         else:
#             if (via_y<(pin_y-2) and iconn[1]>0) or (via_y>(pin_y+2) and iconn[1]<0):
#                 _trc.append((via_x, via_y, trc_width, trc_width))    
#             else:
#                 _sgn_x = 1
#                 _sgn_y = 1
#                 if (iconn[1]>0 and iconn[0]<segm_def[1][0]):
#                     _x = pin_x
#                     _y = pin_y-_sgn_y*segm1
#                     _trc.append((_x, _y, trc_width, trc_width))    
#                     _x = pin_x+_sgn_x*segm1*math.sin(45*math.pi/180)
#                     _y = pin_y+_sgn_y*(-segm1-2*segm1*math.cos(45*math.pi/180))
#                     _trc.append((_x, _y, trc_width, trc_width))    
#                     _x = pin_x+_sgn_x*(segm1+segm1*math.sin(45*math.pi/180)+pin_dx+5)
#                     _trc.append((_x, _y, trc_width, trc_width))    
#                     _x = pin_x+_sgn_x*(segm1+2.5*segm1*math.sin(45*math.pi/180)+pin_dx+5)
#                     _y = pin_y-_sgn_y*segm1
#                     _trc.append((_x, _y, trc_width, trc_width))    
#                     _y = str_line_def[_istr][0]*_x+ str_line_def[_istr][1]
#                     _trc.append((_x, _y, trc_width, trc_width))    
#                     segm1 = segm1 + 0.5*math.sin(22.5*math.pi/180)
#                 else:
#                     _trc.append((pin_x, pin_y-3, trc_width, trc_width))    
        
#         # _trc.append((via_x, via_y, trc_width, trc_width))
#         # via_centers[-1].append((via_x,via_y))
#         # msp.add_circle((via_x, via_y), via_radius, dxfattribs={'layer': 'Vias'})

#         msp.add_lwpolyline(_trc, dxfattribs={'layer': 'Strip gaps'})

#------------------------------------------------
#                Via locations 
#------------------------------------------------

via_file = open(board+'_via_centers.js','w')
via_file.write('function CreateViaArray() {\n');
via_centers = []
for iseg in range(nEtaSegm):
    via_centers.append([])
    # determine strip width at desired radius for lowest lying strip, here the via would be in the narrowest portion
    this_width = 2*(str_line_def[-1][0]*via_row_radii[iseg]+str_line_def[-1][0])
    str_width = (this_width - (nStripsPerConn*nConnPerRow+1)*gap)/(nStripsPerConn*nConnPerRow*1.)    
    for istr in range(nStripsPerConn*nConnPerRow):
        # get via center
        _x0,_y0,_x1,_y1 = 0, 0, 0, 0
        if (str_width>2*(via_radius)): # single row
            _x0,_y0,_x1,_y1 = getLineCircleIntercept(0,0,via_row_radii[iseg],str_line_def[istr][0], str_line_def[istr][1])
        else: # strips too thin, zig-zag
            if (istr%2==0):
                _x0,_y0,_x1,_y1 = getLineCircleIntercept(0,0,via_row_radii[iseg]-2*via_radius,str_line_def[istr][0], str_line_def[istr][1])
            else:
                _x0,_y0,_x1,_y1 = getLineCircleIntercept(0,0,via_row_radii[iseg]+2*via_radius,str_line_def[istr][0], str_line_def[istr][1])
        via_x, via_y = _x0, _y0
        if (_x0<0): via_x, via_y = _x1, _y1
        via_centers[-1].append((via_x,via_y))
        # draw vias for reference
        if (board!="ME0" or abs(_y0)<bites[-1][0][1]): # if within the y coordinate of bite
            if (draw_via_rows): msp.add_circle((via_x, via_y), via_radius, dxfattribs={'layer': 'Vias'})
            via_file.write("   x.push({:.10}); y.push({:.10});\n".format(round(via_x,4), round(via_y,4)))
via_file.write('}\n');
via_file.close()

#------------------------------------------------
#   Draw strip gaps taking into account vias
#------------------------------------------------
if (draw_gaps):
    for istr in range(nStripsPerConn*nConnPerRow+1):
        # list of points to  define strip gap
        this_str = [gap_pts_lo[istr]]
        # loop over eta segments to find via overlaps
        for iseg in range(nEtaSegm):
            this_width = 2*(str_line_def[-1][0]*via_row_radii[iseg]+str_line_def[-1][0])
            str_width = (this_width - (nStripsPerConn*nConnPerRow+1)*gap)/(nStripsPerConn*nConnPerRow*1.) 
            # overlaps
            if (str_width>2*(via_radius)):
                continue
            else:
                # adding gap/2 to radius to account for thickness of gap
                via_eff_radius = via_radius+gap/2.
                # intersection with last via 
                _x2,_y2,_x3,_y3,_x4,_y4,_x5,_y5 = -1e10,-1e10,-1e10,-1e10,-1e10,-1e10,-1e10,-1e10
                if (istr>0):
                    _x2,_y2,_x3,_y3 = getLineCircleIntercept(via_centers[iseg][istr-1][0],via_centers[iseg][istr-1][1],via_eff_radius,gap_line_def[istr][0], gap_line_def[istr][1])
                    dist = 0.5*math.sqrt((_x3-_x2)*(_x3-_x2) + (_y3-_y2)*(_y3-_y2))
                    bulge1 = -(via_eff_radius - math.sqrt(via_eff_radius*via_eff_radius - dist*dist))/dist
                # intersection with next via
                if (istr<nStripsPerConn*nConnPerRow-1):
                    _x4,_y4,_x5,_y5 = getLineCircleIntercept(via_centers[iseg][istr][0],via_centers[iseg][istr][1],via_eff_radius,gap_line_def[istr][0], gap_line_def[istr][1])
                    dist = 0.5*math.sqrt((_x5-_x4)*(_x5-_x4) + (_y5-_y4)*(_y5-_y4))
                    bulge2 = (via_eff_radius - math.sqrt(via_eff_radius*via_eff_radius - dist*dist))/dist
                # by definition of the intercept function _x2<_x3 and _x4<_x5
                if (_x2<_x4):
                    if (istr>0):
                        this_str.append((_x2, _y2, gap, gap, bulge1))
                        this_str.append((_x3, _y3, gap, gap))
                    if (istr<nStripsPerConn*nConnPerRow-1):
                        this_str.append((_x4, _y4, gap, gap, bulge2))
                        this_str.append((_x5, _y5, gap, gap))
                else:
                    if (istr<nStripsPerConn*nConnPerRow-1):
                        this_str.append((_x4, _y4, gap, gap, bulge2))
                        this_str.append((_x5, _y5, gap, gap))    
                    if (istr>0):
                        this_str.append((_x2, _y2, gap, gap, bulge1))
                        this_str.append((_x3, _y3, gap, gap))                

        # add last point and draw gap
        this_str.append(gap_pts_hi[istr])
        msp.add_lwpolyline(this_str, dxfattribs={'layer': 'Strip gaps'})

# gaps between eta segments
for iseg in range(nEtaSegm+1):
    if (iseg==0):
        msp.add_lwpolyline([(segm_def[iseg][0]-gap/2,segm_def[iseg][1], gap, gap), (segm_def[iseg][0]-gap/2, -segm_def[iseg][1], gap, gap)], dxfattribs={'layer': 'Strip gaps'})
    elif (iseg==nEtaSegm):   
        msp.add_lwpolyline([(segm_def[iseg][0]+gap/2,segm_def[iseg][1], gap, gap), (segm_def[iseg][0]+gap/2, -segm_def[iseg][1], gap, gap)], dxfattribs={'layer': 'Strip gaps'})
    else:
        msp.add_lwpolyline([(segm_def[iseg][0],segm_def[iseg][1], gap, gap), (segm_def[iseg][0], -segm_def[iseg][1], gap, gap)], dxfattribs={'layer': 'Strip gaps'})

# add boundary at bites
for ibite in bites:  
    if (draw_gaps): msp.add_lwpolyline(ibite, dxfattribs={'layer': 'Strip gaps'})


# --------------------------------------------------------------
#       Debug
# --------------------------------------------------------------

# print some info for debug
# block = dwg.blocks.get(block_label)  # get all INSERT entities with entity.dxf.name == "Part12"
# print block.name
# for e in block:
#     if e.dxftype()=='LINE':
#         print e.dxf.color, e.dxf.linetype, e.dxf.start, e.dxf.end

dwg.saveas("out/"+board+".dxf")
