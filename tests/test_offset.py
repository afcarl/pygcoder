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
p0 = svg.path.Path()
p1 = svg.path.Path()
for c in pp:
    if isinstance(c, svg.path.CubicBezier):
        p0.extend(pygcoder.parser.bezier.offset_curve(c, 10))
        p1.extend(pygcoder.parser.bezier.offset_curve(c, -10))
    else:
        p0.append(c)
        p1.append(c)

path0 = copy.copy(path)
path1 = copy.copy(path)

for op in (path0, path1):
    for a in op.attrib:
        if nss['inkscape'] in a:
            del op.attrib[a]
        if nss['sodipodi'] in a:
            del op.attrib[a]

path0.attrib['d'] = p0.d()
path1.attrib['d'] = p1.d()

path0.attrib['id'] = 'path0'
path1.attrib['id'] = 'path1'

parent = path.getparent()
parent.append(path0)
parent.append(path1)


xml.write('offset.svg')
