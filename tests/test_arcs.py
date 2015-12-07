#!/usr/bin/env python

import copy

import lxml.etree
import svg.path

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
        p0.append(c)
        p1.append(c)

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


xml.write('arcs.svg')
