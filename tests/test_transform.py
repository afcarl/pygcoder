#!/usr/bin/env python

import lxml.etree

import pygcoder.parser.path

# load drawing.svg
xml = lxml.etree.parse('drawing.svg')
nss = xml.getroot().nsmap
del nss[None]

# transform paths
paths = xml.xpath('//svg:path', namespaces=nss)
for path in paths:
    tpath = pygcoder.parser.path.from_svg(path)
    # re-add paths
    path.attrib['d'] = tpath.d()
    if 'transform' in path.attrib:
        del path.attrib['transform']
    for a in path.attrib:
        if nss['inkscape'] in a:
            del path.attrib[a]
        if nss['sodipodi'] in a:
            del path.attrib[a]
    parent = path.getparent()
    while parent is not None:
        if 'transform' in parent.attrib:
            del parent.attrib['transform']
        parent = parent.getparent()

# save as flattened.svg
xml.write('modified.svg')
