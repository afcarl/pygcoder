#!/usr/bin/env python

import math

import svg.path

NRRF_PRECISION = 0.000001
LUT_RESOLUTION = 401  # based on 3rd order


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


def get_1st_derivative(t, curve):
    # only for cubic (order 3)
    p0 = curve.start
    p1 = curve.control1
    if p0 == p1 and t == 0.:
        return get_1st_derivative(0.000001, curve)
    p2 = curve.control2
    p3 = curve.end
    if p2 == p3 and t == 1.:
        return get_1st_derivative(0.999999, curve)
    return (
        3 * (1 - t) ** 2 * (p1 - p0) +
        6 * (1 - t) * t * (p2 - p1) +
        3 * t ** 2 * (p3 - p2))


def get_2nd_derivative(t, curve):
    # only works for cubic (order 3)
    p0 = curve.start
    p1 = curve.control1
    p2 = curve.control2
    p3 = curve.end
    return (
        6 * (1 - t) * (p2 - 2 * p1 + p0) +
        6 * t * (p3 - 2 * p2 + p1))


def get_derivative(derivative, t, values):
    n = len(values) - 1
    if n == 0:
        return 0
    if derivative == 0:
        value = 0
        for i in xrange(n+1):
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
        return []
    if len(values) - derivative == 2:
        vs = values[:]
        while len(vs) > 2:
            v2 = []
            n = len(vs) - 1
            for i in xrange(n):
                v2.append((vs[i + 1] - vs[i]) * n)
            vs = v2
        if len(vs) < 2:
            return []
        root = map_value(0, vs[0], vs[1], 0., 1.)
        if root < 0 or root > 1:
            return []
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
    pts = [curve.start, curve.control1, curve.control2, curve.end]
    xs = [p.real for p in pts]
    ys = [p.imag for p in pts]
    for root in find_all_roots(1, xs):
        if 0 <= root and root <= 1:
            t_values.append(root)
    for root in find_all_roots(1, ys):
        if 0 <= root and root <= 1:
            t_values.append(root)
    if order > 2:
        for root in find_all_roots(2, xs):
            if 0 <= root and root <= 1:
                t_values.append(root)
        for root in find_all_roots(2, ys):
            if 0 <= root and root <= 1:
                t_values.append(root)
    ts = sorted(list(set(t_values)))
    if len(ts) > 2 * order + 2:
        raise ValueError("Too many roots: %s" % len(ts))
    return ts


def split_curve(curve, t0, t1=None):
    if t1 is None:
        t = t0
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
    if t0 == 0.:
        return split_curve(curve, t1)[0]
    if t1 == 1.:
        return split_curve(curve, t0)[1]
    t2 = (t1 - t0)/(1. - t0)
    return split_curve(split_curve(curve, t0)[1], t2)[0]


def get_all_inflections(curve, l=0., r=1.):
    pts = []
    w = r - l
    ipts = [(i * w) + l for i in get_inflections(align(curve))]
    ipts = ipts[1:-1]  # remove 0 and 1
    if len(ipts) > 3:
        c0, c1 = split_curve(curve, 0.5)
        pts.extend(get_all_inflections(c0, l, l + w * 0.5))
        pts.extend(get_all_inflections(c1, l + w * 0.5, r))
    else:
        pts.extend(ipts)
    return sorted(list(set(pts)))


def add_slices(slices, curve):
    #ipts = get_inflections(align(curve))
    ipts = get_inflections(curve)
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
    #ipts = get_inflections(align(curve))
    ipts = get_inflections(curve)
    # split curve at inflection points
    slices = []
    for i in xrange(len(ipts) - 1):
        slices = add_slices(slices, split_curve(curve, ipts[i], ipts[i+1]))
    return slices


def project_point(point, curve, precision=0.0001):
    mindist = float('inf')
    mint = -1
    for i in xrange(LUT_RESOLUTION):
        t = i / (LUT_RESOLUTION - 1.)
        pp = curve.point(t)
        dist = abs(pp - point)
        if dist < mindist:
            mint = t
            mindist = dist
    step = 0.5 / (LUT_RESOLUTION - 1.)
    i = 0
    while step > precision:
        # refine projection
        # check dist @ .5 LUT res in both directions
        upt = min(mint + step, 1.0)
        downt = max(mint - step, 0.)
        upd = abs(curve.point(upt) - point)
        downd = abs(curve.point(downt) - point)
        # recalculate mint and mindist
        if upd < downd:
            if upd < mindist:
                mint = upt
                mindist = upd
            else:
                step /= 2.
        else:
            if downd < mindist:
                mint = downt
                mindist = downd
            else:
                step /= 2.
        if i == 10:
            break
        i += 1
    return mint


def ratios(curve):
    pass


def compute_normal(t, curve):
    #pts = [curve.start, curve.control1, curve.control2, curve.end]
    #xs = [p.real for p in pts]
    #ys = [p.imag for p in pts]
    #dx = get_1st_derivative(t, xs)
    #dy = get_1st_derivative(t, ys)
    #dx = get_1st_derivative(t, xs)
    #dy = get_1st_derivative(t, ys)
    #dx = get_derivative(1, t, xs)
    #dy = get_derivative(1, t, ys)
    d = get_1st_derivative(t, curve)
    dx = d.real
    dy = d.imag
    a = -math.pi/2.
    ca = math.cos(a)
    sa = math.sin(a)
    nx = dx * ca - dy * sa
    ny = dx * sa + dy * ca
    dst = math.sqrt(nx * nx + ny * ny)
    return complex(nx / dst, ny / dst)


def normals(curve):
    return [
        compute_normal(0, curve),
        compute_normal(project_point(curve.control1, curve), curve),
        compute_normal(project_point(curve.control2, curve), curve),
        compute_normal(1., curve),
    ]


def simple_offset(curve, distance):
    ns = normals(curve)
    pts = [curve.start, curve.control1, curve.control2, curve.end]
    npts = []
    for (p, n) in zip(pts, ns):
        npts.append(p + distance * n)
    return svg.path.CubicBezier(*npts)


def make_offset_array(slices):
    pass


def offset(curve, distance):
    # get slices
    # for each slice, do a simple offset
    slices = [simple_offset(s, distance) for s in get_slices(curve)]
    # the array of slices
    # TODO 'pull' together slices
    # return array of slices
    return slices


def offset_curve2(curve, distance):
    inds = get_all_inflections(curve)
    inds.insert(0, 0.)
    inds.append(1.)
    print inds
    opts = [curve.point(i) + distance * compute_normal(i, curve) for i in inds]
    curves = []
    for i in xrange(len(inds) - 1):
        c = split_curve(curve, inds[i], inds[i+1])
        c.start = opts[i]
        c.end = opts[i+1]
        n1 = compute_normal(project_point(c.control1, curve), curve)
        n2 = compute_normal(project_point(c.control2, curve), curve)
        c.control1 = c.control1 + distance * n1
        c.control2 = c.control2 + distance * n2
        curves.append(c)
    return curves


def offset_curve(curve, distance):
    # split at points (to generate control points)
    slices = get_slices(curve)
    oslices = [simple_offset(s, distance) for s in get_slices(curve)]
    # get inflection points
    ipts = []
    for s in slices:
        ipts.append(s.start)
    ipts.append(s.end)
    # offset inflection points by curve normal
    opts = []
    for ipt in ipts:
        i = project_point(ipt, curve)
        n = compute_normal(i, curve)
        opts.append(ipt + distance * n)
    # copy over offset points to splits
    # ns = len(slices)
    # ni = len(ipts)
    # ns = ni - 1
    for i in xrange(len(oslices)):
        oslices[i].start = opts[i]
        oslices[i].end = opts[i+1]
    return oslices


def to_arc(curve, start=0., end=1.):
    # break up a bezier curve into arcs (and lines)
    # start with points [0, 0.5, 1.], check error, repeat
    midpoint = float(end + start) / 2.
    p0 = curve.point(start)
    p1 = curve.point(midpoint)
    p2 = curve.point(end)
    m0 = -(p1.real - p0.real) / (p1.imag - p0.imag)
    m1 = -(p2.real - p1.real) / (p2.imag - p1.imag)
    c0 = (p1 + p0) / 2.
    c1 = (p2 + p1) / 2.
    b0 = c0.imag - m0 * c0.real
    b1 = c1.imag - m1 * c1.real
    xi = (b1 - b0) / (m0 - m1)
    yi = m0 * xi + b0
    c = complex(xi, yi)
    r = abs(p0 - c)
    #r = ((p0.real - xi) ** 2. + (p0.imag - yi) ** 2.) ** 0.5
    t0 = curve.point((start + midpoint) / 2.)
    t1 = curve.point((midpoint + end) / 2.)
    d0 = abs(abs(t0 - c) - r)
    d1 = abs(abs(t1 - c) - r)
    return p0, p2, xi, yi, r, d0, d1


def split_into_arcs(curve, threshold=0.0001, start=0., end=1.):
    mp = (start + end) / 2.
    arcs = []
    a0 = to_arc(curve, start, mp)
    a1 = to_arc(curve, mp, end)
    if a0[5] < threshold and a0[6] < threshold:
        arcs.append(a0)
    else:
        arcs += split_into_arcs(curve, threshold, start, mp)
    if a1[5] < threshold and a1[6] < threshold:
        arcs.append(a1)
    else:
        arcs += split_into_arcs(curve, threshold, mp, end)
    return arcs


def to_arcs(curve, threshold=0.0001, start=0., end=1.):
    # convert r to ijk relative center for gcode
    # keep as r for svg
    # check against threshold and further subdivide if necessary
    a = to_arc(curve, start, end)
    if a[5] < threshold and a[6] < threshold:
        return [a, ]
    return split_into_arcs(curve, threshold, start, end)


def to_svg_arcs(curve, threshold=0.0001, start=0., end=1.):
    arcs = to_arcs(curve, threshold, start, end)
    return [
        svg.path.Arc(a[0], complex(a[4], a[4]), 0., 0, 0, a[1])
        for a in arcs]
