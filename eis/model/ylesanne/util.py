"Abifunktsioonid"

import re
import eiscore.const as const
import logging
log = logging.getLogger(__name__)

def cx(koordinaadid, kujund):
    p = re.compile(r'\[(-?[0-9\.]+),(-?[0-9\.]+)\]')
    m = p.findall(koordinaadid)
    if m:
        li = [float(pt[0]) for pt in m]
        return sum(li)/len(li)

def cy(koordinaadid, kujund):
    p = re.compile(r'\[(-?[0-9\.]+),(-?[0-9\.]+)\]')
    m = p.findall(koordinaadid)
    if m:
        li = [float(pt[1]) for pt in m]
        return sum(li)/len(li)

def border_pos(koordinaadid, kujund):
    p = re.compile(r'\[(-?[0-9\.]+),(-?[0-9\.]+)\]')
    m = p.findall(koordinaadid)
    if m:
        li_x = [float(pt[0]) for pt in m]
        li_y = [float(pt[1]) for pt in m]
        cx = sum(li_x)/len(li_x)
        cy = sum(li_y)/len(li_y)
        left = min(li_x)
        right = max(li_x)
        top = min(li_y)
        bottom = max(li_y)
        return cx, cy, left, right, top, bottom

def coords_to_list(koordinaadid):
    # koordinaadid on EISis kujul "[[x1,y1],[x2,y2]]"
    # teeme listiks [(x1,y1),(x2,y2)]
    li = []
    for point in re.findall(r'\[([^\[\]]+)\]', koordinaadid):
        x, y = point.split(',')
        li.append((float(x),float(y)))
    return li

def point_in_poly(x, y, koordinaadid):
    """Kontrollitakse, kas punkt asub polügooni sees.
    """
    p = re.compile(r'\[(-?[0-9\.]+),(-?[0-9\.]+)\]')
    m = p.findall(koordinaadid)    
    #log.debug('point_in_poly: (%s,%s)' % (x,y))
    if m:
        npol = len(m)
        xx = [float(pt[0]) for pt in m]
        yy = [float(pt[1]) for pt in m]
        i = 0
        j = npol - 1

        rc = False
        while i < npol:
            if (yy[i] <= y and y < yy[j] or yy[j] <= y and y < yy[i]) and \
                    (x < (xx[j]-xx[i]) * (y-yy[i])/(yy[j]-yy[i]) + xx[i]):
                rc = not rc
            j = i
            i += 1
        return rc

def point_in_shape(x, y, koordinaadid, kujund):
    # x ja y on arvud, koordinaadid on tekst
    if kujund == const.SHAPE_POLY or kujund == const.SHAPE_FREEHAND:
        return point_in_poly(x, y, koordinaadid)

    p = re.compile(r'\[\[([0-9\.]+),([0-9\.]+)\],\[([0-9\.]+),([0-9\.]+)\]\]')
    m = p.match(koordinaadid)
    if m:
        numbers = [float(n) for n in m.groups()]
        (x1, y1, x2, y2) = numbers
        if kujund == const.SHAPE_ELLIPSE or kujund == const.SHAPE_CIRCLE:
            width = x2 - x1
            height = y2 - y1
            if width == 0 or height == 0:
                rc = False
            else:
                aspect = height / width
                xc = (x1 + x2) / 2
                yc = (y1 + y2) / 2
                dx = (x - xc) * aspect
                dy = (y - yc)
                rc = dx*dx + dy*dy < height*height / 4
        else:
            rc = min(x1, x2) <= x <= max(x1, x2) and \
                 min(y1, y2) <= y <= max(y1, y2)
            #log.debug('(%s,%s) in [[%s,%s],[%s,%s]] = %s' % (x,y,x1,y1,x2,y2, rc))
        return rc
