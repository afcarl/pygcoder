#!/usr/bin/env python

import re

import affine


match_string = '([a-zA-Z]+)\(([0-9,.\- ]+)\)'


def rotate(angle, px=None, py=None):
    if px is None:
        pivot = None
    else:
        pivot = (px, py)
    return affine.Affine.rotation(angle, pivot)


transforms = {
    'matrix': affine.Affine,
    'translate': lambda x, y=0.: affine.Affine.translation(x, y),
    'scale': affine.Affine.scale,
    'rotate': rotate,
    'skewX': affine.Affine.shear,
    'skewY': lambda v: affine.Affine.shear(0, v),
}


def to_args(s):
    sc = None
    if ',' in s:
        sc = ','
    return map(lambda ss: float(ss.strip()), s.split(sc))


def from_string(s):
    """Returns a list of transforms"""
    tss = re.findall(s, match_string)
    return [transforms[tn](*to_args(ts)) for tn, ts in tss]


def resolve(*transforms):
    rev = lambda a, b: b * a
    return reduce(rev, transforms, affine.identity)
