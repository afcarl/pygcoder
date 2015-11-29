#!/usr/bin/env python

import copy

import lxml.etree
import svg.path

import pygcoder.parser.bezier
import pygcoder.parser.path

# load drawing.svg
xml = lxml.etree.parse('simple.svg')
nss = xml.getroot().nsmap
del nss[None]

# transform path
path = xml.xpath('//svg:path', namespaces=nss)[0]
pp = pygcoder.parser.path.from_svg(path)
sp = svg.path.Path()
for c in pp:
    if isinstance(c, svg.path.CubicBezier):
        arcs = pygcoder.parser.bezier.to_arcs(c, threshold=0.1)
        # convert to svg arcs
        for a in arcs:
            sp.append(
                svg.path.Arc(a[0], complex(a[4], a[4]), 0., 0, 0, a[1]))
    else:
        sp.append(c)

spath = copy.copy(path)
qpath = copy.copy(path)

for op in (spath,):
    for a in op.attrib:
        if nss['inkscape'] in a:
            del op.attrib[a]
        if nss['sodipodi'] in a:
            del op.attrib[a]

spath.attrib['d'] = sp.d()

spath.attrib['id'] = 'spath'

parent = path.getparent()
parent.append(spath)


xml.write('arcs.svg')
