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
board = 'ME0'

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
nConnPerRow = 3
nStripsPerConn = 128
gap = 0.2
via_radius = 0.3
if (board!="ME0"):
    nEtaSegm = 2
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

original_dwg = ezdxf.readfile("in/"+board+"_outline.dxf")
dwg = ezdxf.new(dxfversion=original_dwg.dxfversion)
msp = dwg.modelspace()
dwg.layers.new(name='Strip gaps', dxfattribs={'linetype': 'Continuous', 'color': 40})
dwg.layers.new(name='Strips', dxfattribs={'linetype': 'DASHED', 'color': 222})
dwg.layers.new(name='Vias', dxfattribs={'linetype': 'Continuous', 'color': 10})

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

# copy board from the original DXF and paste it into the new one
importer = ezdxf.Importer(original_dwg, dwg)
importer.import_blocks(query=block_label, conflict='discard')
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
    importer = ezdxf.Importer(chimney_dwg, dwg)
    importer.import_blocks(query=chimney_label, conflict='discard')
    board_rotation = -90.
    msp.add_blockref(chimney_label,(0,0), dxfattribs={
            'xscale': 1.,
            'yscale': 1.,
            'rotation': board_rotation
        })

# edit an existing polyline
# line = msp.query('LWPOLYLINE')[0]

# building strips
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


# strips
for i in range(nStripsPerConn*nConnPerRow):
    str_lo_x = segm_def[0][0]
    str_lo_y = i*(str_width_lo+gap) + gap + str_width_lo/2. - width_lo/2.
    str_hi_x = segm_def[-1][0]
    str_hi_y = i*(str_width_hi+gap) + gap + str_width_hi/2. - width_hi/2.
    _a,_b = getLineDef(str_lo_x, str_lo_y, str_hi_x, str_hi_y)
    str_line_def.append([_a, _b])
    if (debug): msp.add_lwpolyline([(0, _b),(1500, _a*1500+_b)], dxfattribs={'layer': 'Strip gaps'})

# add via rows - saving center positions for later
via_file = open("via_coord/"+board+'_via_centers.js','w')
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
            msp.add_circle((via_x, via_y), via_radius, dxfattribs={'layer': 'Vias'})
            via_file.write("   x.push({:.10}); y.push({:.10});\n".format(round(via_x,4), round(via_y,4)))
via_file.write('}\n');
via_file.close()

# draw gaps
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
    msp.add_lwpolyline(ibite, dxfattribs={'layer': 'Strip gaps'})

# print some info for debug
# block = dwg.blocks.get(block_label)  # get all INSERT entities with entity.dxf.name == "Part12"
# print block.name
# for e in block:
#     if e.dxftype()=='LINE':
#         print e.dxf.color, e.dxf.linetype, e.dxf.start, e.dxf.end

outfile = "out/"+board+".dxf"
dwg.saveas(outfile)
print "   open "+outfile

