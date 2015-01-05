#!/usr/bin/env python

import copy
import math

import svg.path

from . import transform


def transform_point(t, p):
    np = t * [[p.real, ], [p.imag, ], [1, ]]
    return float(np[0, 0]) + float(np[1, 0]) * 1j


def transform_radius(t, r):
    # http://stackoverflow.com/questions/5149301/baking-transforms-into-svg-path-element-commands
    # only works for uniform scaling
    # maybe copy from here: https://gist.github.com/timo22345/9413158
    sx = math.sqrt(
        float(t[0, 0]) * float(t[0, 0]) + float(t[0, 1]) * float(t[0, 1]))
    sy = math.sqrt(
        float(t[1, 0]) * float(t[1, 0]) + float(t[1, 1]) * float(t[1, 1]))
    return r.real * sx + r.imag * sy * 1j


def transform_rotation(t, r):
    rot = math.atan2(float(t[1, 0]), float(t[1, 1])) * 180. / math.pi
    return r + rot


def transform_path(path, transforms):
    if len(transforms) == 0:
        return path
    t = transform.resolve(*transforms)
    # TODO
    # apply transforms to path
    new_path = svg.path.Path()
    for e in path:
        ce = copy.copy(e)
        # monkey patch class
        ce.tpoint = lambda v, t=t, self=ce: transform_point(t, self.point(v))
        if isinstance(e, svg.path.Line):
            ce.start = transform_point(t, e.start)
            ce.end = transform_point(t, e.end)
        elif isinstance(e, svg.path.CubicBezier):
            ce.start = transform_point(t, e.start)
            ce.end = transform_point(t, e.end)
            ce.control1 = transform_point(t, e.control1)
            ce.control2 = transform_point(t, e.control2)
        elif isinstance(e, svg.path.QuadraticBezier):
            ce.start = transform_point(t, e.start)
            ce.end = transform_point(t, e.end)
            ce.control = transform_point(t, e.control)
        elif isinstance(e, svg.path.Arc):
            ce.start = transform_point(t, e.start)
            ce.end = transform_point(t, e.end)
            # how to transform radius?? ce.radius (complex)
            ce.radius = transform_radius(t, e.radius)
            # how to transform rotation?? ce.rotation
            ce.rotation = transform_rotation(t, e.rotation)
        else:
            raise Exception("Unknown type: %s" % type(e))
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
        parent = parent.getparent()
    if len(ts) == 0:
        return path
    # transform path
    return transform_path(path, ts)


def center(path, points_step=10, min_points=100, max_error=0.009,
           max_points=1000):
    error = max_error + 1
    n = float(min_points)
    center = None
    # TODO check if start and end are the same
    while error > max_error:
        if n > max_points:
            raise Exception("center: too many points")
        # evaluate path at n points
        if center is None:
            # find center,
            center = sum([path.point(i / n) for i in xrange(int(n))])
            center = (center.real / n + center.imag / n * 1j)
        # evaluate at n + points_step points
        hrn = n + points_step
        hr = sum([path.point(i / hrn) for i in xrange(int(hrn))])
        hr = (hr.real / hrn + hr.imag / hrn * 1j)
        # measure error
        diff = hr - center
        error = abs(diff.real) + abs(diff.imag)
        print n, error, center
        n += points_step
        center = hr
    # return center evaluated at n
    return center.real, center.imag


def offset(path, radius):
    # get offset code from here:
    # https://github.com/Pomax/bezierinfo/blob/gh-pages/framework/BezierCurve.pde
    pass


def curves_to_lines(path):
    # turn all beziers into lines/arcs
    # algorithm:
    # - bisect: check error (do this a couple times)
    # - if error > threshold, bisect again on 'bad' side(s)
    # check error for both arc and line
    # fit arc by solving linear system from points
    pass


def counterclockwise(path):
    # orient path to be counterclockwise
    pass


def clockwise(path):
    # orient path to be clockwise
    pass
