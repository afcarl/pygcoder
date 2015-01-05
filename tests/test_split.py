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
hp = svg.path.Path()
qp = svg.path.Path()
for c in pp:
    if isinstance(c, svg.path.CubicBezier):
        l, r = pygcoder.parser.bezier.split_curve(c, 0.5)
        hp.append(l)
        hp.append(r)
        l, r = pygcoder.parser.bezier.split_curve(c, 0.25)
        qp.append(l)
        qp.append(r)
    else:
        hp.append(c)
        qp.append(c)

hpath = copy.copy(path)
qpath = copy.copy(path)

for op in (hpath, qpath):
    for a in op.attrib:
        if nss['inkscape'] in a:
            del op.attrib[a]
        if nss['sodipodi'] in a:
            del op.attrib[a]

hpath.attrib['d'] = hp.d()
qpath.attrib['d'] = qp.d()

hpath.attrib['id'] = 'hpath'
qpath.attrib['id'] = 'qpath'

parent = path.getparent()
parent.append(hpath)
parent.append(qpath)


xml.write('split.svg')
