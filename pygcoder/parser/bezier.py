#!/usr/bin/env python

import math

import svg.path

NRRF_PRECISION = 0.000001


def map_value(v, s0, e0, s1, e1):
    return s1 + (e1 - s1) * ((v - s0) / (e0 - s0))


def quadratic_to_cubic(curve):
    # http://stackoverflow.com/questions/3162645/convert-a-quadratic-bezier-to-a-cubic
    if isinstance(curve, svg.path.CubicBezier):
        return curve
    elif isinstance(curve, svg.path.QuadraticBezier):
        raise Exception()
    else:
        raise Exception()


def align(curve, start=None, end=None):
    """Align curve to a line starting at start with angle 0"""
    if not isinstance(curve, svg.path.CubicBezier):
        curve = quadratic_to_cubic(curve)
    if start is None:
        start = curve.start
    if end is None:
        end = curve.end
    angle = math.atan2(end.imag - start.imag, end.real - start.real)
    ca = math.cos(-angle)
    sa = math.sin(-angle)
    ox = start.real
    oy = start.imag
    pts = []
    for p in (curve.start, curve.control1, curve.control2, curve.end):
        x = ca * (p.real - ox) - sa * (p.imag - oy)
        y = sa * (p.real - ox) + ca * (p.imag - oy)
        pts.append(x + y * 1j)
    return svg.path.CubicBezier(*pts)


def binomial(n, k):
    try:
        return math.factorial(n) // math.factorial(k) // math.factorial(n - k)
    except ValueError:
        return 0


def get_derivative(derivative, t, values):
    n = len(values) - 1
    if n == 0:
        return 0
    if derivative == 0:
        value = 0
        for i in xrange(n):
            value += binomial(n, i) * pow(1-t, n-i) * pow(t, i) * values[i]
        return value
    vs = []
    for i in xrange(n):
        vs.append(n * (values[i+1] - values[i]))
    return get_derivative(derivative-1, t, vs)


def find_roots(derivative, t, values, offset=0., depth=0.):
    f = get_derivative(derivative, t, values) - offset
    df = get_derivative(derivative + 1, t, values)
    t2 = t - (f / df)
    if (df == 0.):
        t2 = t - f
    if depth > 12:
        if abs(t - t2) < NRRF_PRECISION:
            return int(t2 / NRRF_PRECISION) * NRRF_PRECISION
        raise Exception("Newton-Raphson ran past recursion depth")
    if abs(t - t2) > NRRF_PRECISION:
        return find_roots(derivative, t2, values, offset, depth + 1)
    return t2


def find_all_roots(derivative, values):
    if len(values) - derivative <= 1:
        return None
    if len(values) - derivative == 2:
        vs = values.copy()
        while len(vs) > 2:
            v2 = []
            n = len(vs) - 1
            for i in xrange(n):
                v2.append((vs[i + 1] - vs[i]) * n)
            vs = v2
        if len(vs) < 2:
            return None
        root = map_value(0, vs[0], vs[1], 0., 1.)
        if root < 0 or root > 1:
            return None
        return [root, ]
    roots = []
    for t in xrange(0, 100, 1):
        t /= 100.
        try:
            root = round(
                find_roots(derivative, t, values) / NRRF_PRECISION
            ) * NRRF_PRECISION
            if root < 0 or root > 1:
                continue
            if abs(root - t) <= NRRF_PRECISION:
                continue
            if root in roots:
                continue
            roots.append(root)
        except:
            continue
    return roots


def get_inflections(curve, order=3):
    """Get all t_values, places where the curve inflects"""
    t_values = [0., 1.]
    pts = [(p.real, p.imag) for p in (p.start, p.control1, p.control2, p.end)]
    xs = [pts[0] for p in pts]
    ys = [pts[1] for p in pts]
    for root in find_all_roots(1, xs):
        if 0 < root and root < 1:
            t_values.append(root)
    for root in find_all_roots(1, ys):
        if 0 < root and root < 1:
            t_values.append(root)
    if order > 2:
        for root in find_all_roots(2, xs):
            if 0 < root and root < 1:
                t_values.append(root)
        for root in find_all_roots(2, ys):
            if 0 < root and root < 1:
                t_values.append(root)
    ts = sorted(list(set(t_values)))
    if len(ts) > 2 * order + 2:
        raise ValueError("Too many roots: %s" % len(ts))
    return ts


def split_curve(curve, t):
    x1, y1 = curve.start.real, curve.start.imag
    x2, y2 = curve.control1.real, curve.control1.imag
    x3, y3 = curve.control2.real, curve.control2.imag
    x4, y4 = curve.end.real, curve.end.imag

    x12 = (x2-x1)*t+x1
    y12 = (y2-y1)*t+y1

    x23 = (x3-x2)*t+x2
    y23 = (y3-y2)*t+y2

    x34 = (x4-x3)*t+x3
    y34 = (y4-y3)*t+y3

    x123 = (x23-x12)*t+x12
    y123 = (y23-y12)*t+y12

    x234 = (x34-x23)*t+x23
    y234 = (y34-y23)*t+y23

    x1234 = (x234-x123)*t+x123
    y1234 = (y234-y123)*t+y123

    l = svg.path.CubicBezier(
        x1 + y1 * 1j, x12 + y12 * 1j, x123 + y123 * 1j, x1234 + y1234 * 1j)
    r = svg.path.CubicBezier(
        x1234 + y1234 * 1j, x234 + y234 * 1j, x34 + y34 * 1j, x4 + y4 * 1j)
    return l, r


def add_slices(slices, curve):
    ipts = get_inflections(align(curve))
    if len(ipts) > 3:
        # further subdivide
        c0, c1 = split_curve(curve, 0.5)
        slices.append(c0)
        slices.append(c1)
    else:
        slices.append(curve)
    return slices


def get_slices(curve):
    # align, get inflection points
    ipts = get_inflections(align(curve))
    # split curve at inflection points
    slices = []
    for i in xrange(len(ipts) - 1):
        slices = add_slices(slices, split_curve(ipts[i], ipts[i+1]))
    return slices


def simple_offset(curve, distance):
    # needs: ratios, normals
    pass


def make_offset_array(slices):
    pass


def offset(curve, distance):
    # get slices
    # for each slice, do a simple offset
    # the array of slices
    # 'pull' together slices
    # return array of slices
    pass
