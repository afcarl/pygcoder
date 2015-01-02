#!/usr/bin/env python

import re

import numpy
# affine appears to have a major bug and incorrectly applies
# matrices to points, so... use numpy


match_string = '([a-zA-Z]+)\(([0-9,.\- ]+)\)'


def matrix(a, b, c, d, e, f):
    return numpy.matrix([[a, c, e], [b, d, f], [0., 0., 1.]])


def translate(x, y):
    return numpy.matrix([[1., 0., x], [0., 1., y], [0., 0., 1.]])


def scale(x, y=1.):
    return numpy.matrix([[x, 0., 0.], [0., y, 0.], [0., 0., 1.]])


def rotate(a, x=0., y=0.):
    ra = numpy.radians(a)
    r = numpy.matrix([
        [numpy.cos(ra), -numpy.sin(ra), 0.],
        [numpy.sin(ra), numpy.cos(ra), 0.],
        [0., 0., 1.]])
    if x == 0. and y == 0.:
        return r
    return translate(-x, -y) * r * translate(x, y)


def skew_x(a):
    ra = numpy.radians(a)
    return numpy.matrix([
        [1., numpy.tan(ra), 0.],
        [0., 1., 0.],
        [0., 0., 1.]])


def skew_y(a):
    ra = numpy.radians(a)
    return numpy.matrix([
        [1., 0., 0.],
        [numpy.tan(ra), 1., 0.],
        [0., 0., 1.]])


transforms = {
    'matrix': matrix,
    'translate': translate,
    'scale': scale,
    'rotate': rotate,
    'skewX': skew_x,
    'skewY': skew_y,
}


def to_args(s):
    sc = None
    if ',' in s:
        sc = ','
    return map(lambda ss: float(ss.strip()), s.split(sc))


def from_string(s):
    """Returns a list of transforms"""
    tss = re.findall(match_string, s)
    return [transforms[tn](*to_args(ts)) for tn, ts in tss]


def resolve(*transforms):
    if len(transforms) == 1:
        return transforms[0]
    i = numpy.matrix([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
    if len(transforms) == 0:
        return i
    rev = lambda a, b: b * a
    return reduce(rev, transforms, i)
