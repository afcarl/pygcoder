#!/usr/bin/env python

import lxml.etree

from .. import parser


def load_paths(fn):
    doc = lxml.etree.parse(fn)
    nss = doc.getroot().nsmap.copy()
    del nss[None]

    paths = doc.xpath('//svg:path', namespaces=nss)
    return [parser.path.from_svg(path) for path in paths]
