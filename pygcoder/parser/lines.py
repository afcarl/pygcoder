#!/usr/bin/env python

import svg.path


def offset(l, distance):
    d = abs(l.end - l.start)
    n0 = -(l.end.real - l.start.real)/(l.end.imag - l.start.imag)/d
    return svg.path.Line(
        l.start + n0 * d,
        l.end + n0 * d)
