#!/usr/bin/env python

import copy

import affine
import svg.path

from . import transform


def transform_point(t, p):
    np = t * (p.real, p.imag)
    return np[0] + np[1] * 1j


def transform_path(path, transforms):
    if len(transforms) == 0:
        return path
    t = transform.resovle(*transforms)
    # TODO
    # apply transforms to path
    new_path = svg.path.Path()
    for e in path:
        ce = copy.copy(e)
        # monkey patch class
        ce.tpoint = lambda v, t=t, self=ce: transform_point(t, self.point(v))
        #if isinstance(svg.path.Line):
        #    ce.start = transform_point(t, e.start)
        #    ce.end = transform_point(t, e.end)
        #elif isinstance(svg.path.CubicBezier):
        #    ce.start = transform_point(t, e.start)
        #    ce.end = transform_point(t, e.end)
        #    ce.control1 = transform_point(t, e.control1)
        #    ce.control2 = transform_point(t, e.control2)
        #elif isinstance(svg.path.QuadraticBezier):
        #    ce.start = transform_point(t, e.start)
        #    ce.end = transform_point(t, e.end)
        #    ce.control = transform_point(t, e.control)
        #elif isinstance(svg.path.Arc):
        #    ce.start = transform_point(t, e.start)
        #    ce.end = transform_point(t, e.end)
        #    # how to scale radius??
        new_path.append(ce)
    # return modified path
    return new_path


def from_svg(element):
    # read path from d
    path = svg.path.parse_path(element.attrib['d'])
    # get transform for element and parents
    if 'transform' in element.attrib:
        ts = transform.from_string(element.attrib['transform'])
    else:
        ts = []
    # get transform from parents
    parent = element.getparent()
    while parent is not None:
        if 'transform' in parent.attrib:
            pts = transform.from_string(parent.attrib['transform'])
            ts = pts + ts
        parent = element.getparent()
    if len(ts) == 0:
        return path
    # transform path
    return transform_path(path, ts)


def center(path):
    pass


def offset(path, radius):
    pass


def curves_to_lines(path):
    # turn all beziers into lines/arcs
    pass


def counterclockwise(path):
    # orient path to be counterclockwise
    pass


def clockwise(path):
    # orient path to be clockwise
    pass
