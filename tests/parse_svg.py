#!/usr/bin/env python

import sys

import lxml.etree
import svg.path

tools = {
    '1/8" endmill': {
        'kerf': 0.0625,
    }
}

operations = {
    '#ff0000': {
        'operation': 'contour',
        'offset': 'inside',
        'tool': '1/8" endmill',
        'depth': 0.25,
        'enter': 'plunge',
        'tabs': True,
    },
    '#00ff00': {
        'operation': 'pocket',
        'tool': '1/8" endmill',
    },
    '#0000ff': {
        'operation': 'drill',
        'peck': True,
    },
}

if len(sys.argv) < 2:
    raise Exception("Must provide filename")

# open file
doc = lxml.etree.parse(sys.argv[1])
nss = doc.getroot().nsmap.copy()
del nss[None]

# find paths
paths = doc.xpath('//svg:path', namespaces=nss)

# resolve operations (styles -> tools)
# compute cuts
# output gcode
