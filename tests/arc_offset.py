#!/usr/bin/env python

import copy

import lxml.etree
import svg.path

import pygcoder.parser.arcs
import pygcoder.parser.bezier
import pygcoder.parser.path


offset_distance = 30.

# load drawing.svg
xml = lxml.etree.parse('simple.svg')
nss = xml.getroot().nsmap
del nss[None]

# transform path
path = xml.xpath('//svg:path', namespaces=nss)[0]
pp = pygcoder.parser.path.from_svg(path)
p0 = svg.path.Path()
p1 = svg.path.Path()
for c in pp:
    if isinstance(c, svg.path.CubicBezier):
        arcs = pygcoder.parser.bezier.to_svg_arcs(c, threshold=0.1)
        # convert to svg arcs
        for a in arcs:
            oa = pygcoder.parser.arcs.offset(a, offset_distance)
            if oa is not None:
                p0.append(oa)
            oa = pygcoder.parser.arcs.offset(a, -offset_distance)
            if oa is not None:
                p1.append(oa)
            #sp.append(
            #    svg.path.Arc(
            #        a[0], complex(a[4], a[4]), 0., 0, 0, a[1]))
    else:
        raise NotImplementedError


# clean up paths
def stitch_path(p):
    np = svg.path.Path()
    np.append(p[0])
    pt = p[0].end
    for s in p[1:]:
        if abs(s.start - pt) > 0.001:
            np.append(svg.path.Line(pt, s.start))
        else:
            s.start = pt
        np.append(s)
        pt = s.end
    return np


def simplify_path(p):
    # find intersections between segments
    # remove segments between intersections
    # adjust start/end to remove intersections
    arcs = [pygcoder.parser.arcs.from_svg_arc(s) for s in p]
    intersections = []
    for (i, a) in enumerate(arcs[:-1]):
        for (j, oa) in enumerate(arcs[i+1:]):
            if a == oa:
                continue
            intersection = a.intersect(oa)
            if intersection:
                intersections.append((i, i+j+1, intersection))
    skips = []
    for i in intersections:
        if i[1] - i[0] != 1:
            j = i[0] + 1
            while j < i[1]:
                skips.append(j)
                j += 1
    np = svg.path.Path()
    for i in xrange(len(p)):
        if i in skips:
            continue
        a = arcs[i]
        s = p[i]
        # TODO do this better!
        for intersection in intersections:
            if len(intersection[2]) != 1:
                raise NotImplementedError()
            if intersection[0] == i:
                # modify the end point to be this point
                s.end = intersection[2][0]
            if intersection[1] == i:
                # modify the start point to be this point
                s.start = intersection[2][0]
        np.append(s)
    return np

#i0 = simplify_path(p0)
#i1 = simplify_path(p1)
#p0 = stitch_path(p0)
#p1 = stitch_path(p1)
p0 = stitch_path(simplify_path(p0))
p1 = stitch_path(simplify_path(p1))

path0 = copy.copy(path)
path1 = copy.copy(path)

for op in (path0, path1,):
    for a in op.attrib:
        if nss['inkscape'] in a:
            del op.attrib[a]
        if nss['sodipodi'] in a:
            del op.attrib[a]

path0.attrib['d'] = p0.d()
path1.attrib['d'] = p1.d()

path0.attrib['id'] = 'path0'
path0.attrib['id'] = 'path1'

parent = path.getparent()
parent.append(path0)
parent.append(path1)


xml.write('arcs_offset.svg')
