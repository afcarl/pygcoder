#!/usr/bin/env python
"""
svg arcs are:
    start : complex
    radius : complex
    rotation
    arc
    sweep (0 ccw, 1 cw)
    end : complex

gcode arcs are:
    start
    stop
    clockwise/counterclockwise
    ijk (center, incremental) or radius

    not sure how it figures out long vs short path with just radius

my arcs are:
    start : complex
    end : complex
    clockwise/counterclockwise
    ijk (center, absolute) : complex

needs functions for:
    finding intersection between two arcs
    finding intersection between and arc and line
    convert from/to svg/gcode format


Ok, some conventions
    angle 0 is 'right'
    angle pi/2 is up
    angle +- pi is left
    angle -pi/2 is down
"""

import math

import svg.path


# default err acceptable when trying to match floats
default_err = 0.000001
pi2 = math.pi * 2


def clamp_angle(angle):
    while angle > math.pi:
        angle -= pi2
    while angle < -math.pi:
        angle += pi2
    return angle


def angle_in_range(angle, start, end, direction):
    if direction:
        return not angle_in_range(angle, start, end, 0)
    start = clamp_angle(start)
    end = clamp_angle(end)
    angle = clamp_angle(angle)
    if end > start:  # wraps
        if angle <= start or angle >= end:
            return True
        else:
            return False
    else:
        if start >= angle >= end:
            return True
        else:
            return False


class Arc(object):
    # TODO make this compatible with svg.path
    def __init__(self, center, start, end, direction):
        """
        start: (complex) starting point of arc
        end: (complex) ending point of arc
        center: (complex) center point of arc
        direction: (0/1) direction of arc
            0 = clockwise
            1 = counterclockwise

        angles are:
            'right' = 0
            'up' = pi / 2
            'left' = +-pi
            'down' = -pi / 2
        """
        self.center = center
        self.start = start
        self.end = end
        self.direction = direction
        self.validate()

    @property
    def radius(self):
        return abs(self.start - self.center)

    def validate(self):
        assert isinstance(self.center, complex)
        assert isinstance(self.start, complex)
        assert isinstance(self.end, complex)
        assert self.radius - abs(self.start - self.center) < default_err
        assert self.radius - abs(self.end - self.center) < default_err
        assert self.direction in (0, 1)

    def to_angle(self, pt):
        d = pt - self.center
        return math.atan2(d.imag, d.real)

    def from_angle(self, angle):
        dy = math.sin(angle)
        dx = math.cos(angle)
        return self.center + complex(dx, dy)

    def test_on_arc(self, pt, err=None):
        if err is None:
            err = default_err
        r = abs(pt - self.center)
        if abs(r - self.radius) > err:
            return False
        a = self.to_angle(pt)
        sa = self.to_angle(self.start)
        ea = self.to_angle(self.end)
        return angle_in_range(a, sa, ea, self.direction)

    def point(self, i):
        assert 0 <= i <= 1.
        sa = self.to_angle(self.start)
        ea = self.to_angle(self.end)
        if self.direction:  # ccw
            # ccw means angle should increase from start -> end
            while ea < sa:
                ea += pi2
            da = (ea - sa) * i
            return self.from_angle(sa + da)
        else:  # cw
            # cw means angle should decrease from start -> end
            while ea > sa:
                ea -= pi2
            da = (sa - ea) * i
            return self.from_angle(sa - da)

    def intersect(self, arc):
        """
        False :
            no intersection
            or one inside the other
        2 points :
            arcs have same radius and overlap
            or intersection points
        1 point :
            intersection point
        """
        d = abs(self.center - arc.center)
        if d > (self.radius + arc.radius):
            return False
        if d < abs(self.radius - arc.radius):
            return False
        if d == 0 and self.radius == arc.radius:
            # check if arcs overlap
            if arc.test_on_arc(self.start):
                p3a = self.start
            elif self.test_on_arc(arc.start):
                p3a = arc.start
            else:
                return False
            if arc.test_on_arc(self.end):
                p3b = self.end
            elif self.test_on_arc(arc.end):
                p3b = arc.end
            else:
                return False
            return [p3a, p3b]
        a = (
            (self.radius * self.radius - arc.radius * arc.radius + d * d)
            / (2 * d))
        p2 = self.center + a * (arc.center - self.center) / d
        if d == (self.radius + arc.radius):
            p3a = p2
            p3b = p2
        else:
            h = math.sqrt(self.radius * self.radius - a * a)
            sy = h * (arc.center.real - self.center.real) / d
            sx = h * (arc.center.imag - self.center.imag) / d
            p3a = complex(
                p2.real + sx, p2.imag - sy)
            p3b = complex(
                p2.real - sx, p2.imag + sy)
        ipts = []
        for p in (p3a, p3b):
            if self.test_on_arc(p) and arc.test_on_arc(p):
                ipts.append(p)
        if not len(ipts):
            return False
        return ipts


def find_circle(p0, p1, p2):
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
    return c, r


def offset(arc, distance):
    mp = arc.point(0.5)
    c, r = find_circle(arc.start, mp, arc.end)
    n0 = (arc.start - c) / r
    n1 = (arc.end - c) / r
    nr = r + distance
    if nr < 0:
        return None
    return svg.path.Arc(
        c + n0 * nr, complex(nr, nr),
        arc.rotation, arc.arc, arc.sweep,
        c + n1 * nr)


def from_svg_arc(arc):
    if isinstance(arc, Arc):
        return arc
    # TODO use better way to find center
    mp = arc.point(0.5)
    c, _ = find_circle(arc.start, mp, arc.end)
    # TODO why isn't direction 1 - sweep?
    return Arc(c, arc.start, arc.end, arc.sweep)


def to_svg_arc(arc):
    if isinstance(arc, svg.path.Arc):
        return arc
    # TODO sort out sweep and arc flags
    sweep = 1 - arc.direction
    arc = 0
    r = arc.radius
    return svg.path.Arc(
        arc.start, complex(r, r), 0., arc, sweep, arc.end)


def to_lines(arc, threshold=0.0001):
    pass
