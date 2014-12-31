#!/usr/bin/env python


class Mover(object):
    def __init__(self, options):
        self.tools = {}
        # clearance height, retract height, conventional/climb?
        self.state = {}  # necessary?

    def header(self):
        pass

    def footer(self):
        pass

    def rapid_to(self, x=None, y=None, z=None):
        # G0
        pass

    def line_to(self, x=None, y=None, z=None):
        # G1
        pass

    def arc_to(self, *args):  # TODO
        # G2/G3
        pass

    def curve_to(self, *args):  # TODO
        # G5 or G5.1
        pass

    def dwell(self, *args):
        # G4
        pass

    def plane(self, *args):
        # G17, G18, G19
        pass

    def units(self, *args):
        # G20 G21
        pass

    # predefined position?
    # TODO other gcodes...

    # ----- operations ----
    def retract(self, **options):
        pass

    def plunge(self, **options):
        pass

    # ramp?
    # helix in?

    def clearance(self, **options):
        pass

    def drill(self, path, **options):
        pass

    def pocket(self, path, **options):
        pass

    def contour(self, path, **options):
        pass
