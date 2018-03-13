#! /usr/bin/env python
import ezdxf

# intersection of a circle (x-a)^2+(y-b)^2 = R^2 and a line y = cx+d
def getLineCircleIntercept(a, b, R, c, d):
    _sqrt = sqrt(-a^2*c^2 + 2*a*b*c - 2*a*c*d - b^2 + 2*b*d + c^2*R^2 - d^2 + R^2)
    x0 = (-_sqrt + a + b*c - c*d)/(c^2 + 1)
    y0 = c*x0 + b
    x1 = (_sqrt + a + b*c - c*d)/(c^2 + 1)
    y1 = c*x1 + b
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

board = 'ME0'
# handles for finding lines on the drawing
active_area_color = 150
chamber_cover_color = 1
segmentation_color = 3

# define segment by the highest point in Y
segm_def = [
  [660.0, 117.588162],
  [727.456, 129.616053],
  [801.892, 142.888528],
  [884.139, 157.553761],
  [975.077, 173.768662],
  [1075.708, 191.711895],
  [1187.178, 211.587799],
  [1310.804, 230.0],
  [1448.0, 230.0]
]

cutout = [
  [1448.0, 230.0], [1290.439116, 230.0]
]

nEtaSegm = 8
nStripsPerConn = 128
nConnPerRow = 3
gap = 0.2

# start point - P1
# end point - P2
# center point - P0

# radius R = distance from P0 to P1
# L = 0.5 * distance from P1 to P2

# bulge = ( R - sqrt(R*R - L*L) ) / L

original_dwg = ezdxf.readfile("ME0-2018.dxf")
dwg = ezdxf.new(dxfversion=original_dwg.dxfversion)
msp = dwg.modelspace()

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
importer.import_blocks(query='BLOCK173', conflict='discard')
msp.add_blockref('BLOCK173',(0,0), dxfattribs={
        'xscale': 1.,
        'yscale': 1.,
        'rotation': 180.
    })

# edit an existing polyline
# line = msp.query('LWPOLYLINE')[0]

# building strips
me0_maxy = 0
if (board == 'ME0'): # do not extrapolate strips all the way due to irregular shape
    _c,_d = getLineDef(segm_def[0][0], segm_def[0][1], segm_def[-3][0], segm_def[-3][1])
    me0_maxy = _c*segm_def[-1][0]+_d
    print me0_maxy

lo_pts, hi_pts = [], []
lo_len = segm_def[0][1]*2.
hi_len = segm_def[-1][1]*2.
if (board=='ME0'):
    hi_len = me0_maxy*2

wlo_strip = (lo_len - (nStripsPerConn*nConnPerRow-1)*gap)/(nStripsPerConn*nConnPerRow*1.)
whi_strip = (hi_len - (nStripsPerConn*nConnPerRow-1)*gap)/(nStripsPerConn*nConnPerRow*1.)
for i in range(nStripsPerConn*nConnPerRow-1):
    lo_pts.append((segm_def[0][0], i*(wlo_strip+gap) + wlo_strip + gap/2. - lo_len/2., gap, gap))
    if (board=='ME0'):
        _x = segm_def[-1][0]
        _y = i*(whi_strip+gap) + whi_strip + gap/2. - hi_len/2.
        if (abs(_y) > segm_def[-1][1]):
            _a,_b = getLineDef(lo_pts[-1][0], lo_pts[-1][1], _x, _y)
            _c,_d = 0, sign(_y)*cutout[0][1] # cutout slope is 0 and intercept is y
            _x,_y = getLineLineIntercept(_a,_b,_c,_d)
        hi_pts.append((_x, _y, gap, gap))
    else:
        hi_pts.append((segm_def[-1][0], i*(whi_strip+gap) + whi_strip + gap/2. - hi_len/2., gap, gap))

for istrip in range(len(lo_pts)):
    msp.add_lwpolyline([lo_pts[istrip], hi_pts[istrip]])

# hatch = msp.add_hatch(color=2)  # by default a solid fill hatch with fill color=7 (white/black)
# with hatch.edit_boundary() as boundary:  # edit boundary path (context manager)
#     # every boundary path is always a 2D element
#     # vertex format for the polyline path is: (x, y[, bulge])
#     # bulge value 1 = an arc with diameter=10 (= distance to next vertex * bulge value)
#     # bulge value > 0 ... arc is right of line
#     # bulge value < 0 ... arc is left of line
#     boundary.add_polyline_path([(660.0, 115.), (660.0, 117.588162), 
#         (727.456, 129.616053), (727.456, 127)], is_closed=1)

# print some info for debug
# block = dwg.blocks.get('BLOCK173')  # get all INSERT entities with entity.dxf.name == "Part12"
# print block.name
# for e in block:
#     if e.dxftype()=='LINE':
#         print e.dxf.color, e.dxf.linetype, e.dxf.start, e.dxf.end

dwg.saveas("test.dxf")
