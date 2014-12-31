Convert svg to gcode. Inspired by gcodetools inkscape extension.

Converts shapes (within workspace) to gcode paths.

Shapes
------

- rectangle
- circle (not used by inkscape)
- ellipse (not used by inkscape)
- path [maybe just start with all paths for now]


Parameters
------

- Depth is set by color.
- Filled objects are milled pockets.
- Inside vs outside also by color?
- Tool set by color


Operations
------

- Drilling (peck drill?)
- Pocket milling (area)
- Contour milling (follow inside/outside path)


Load svg
Find paths within workspace (width/height of svg)
Get color-to-cut mapping for options (or element outside workspace?)
Order operations by tool, then depth (shallowest to deepest)
Process each operation into gcode (split by tool? by depth?)

Operation processing
------

all: clearance z height, retract z height, conventional/climb

Drilling: find center of path (probably circle), peck drill?
Contour: on, outside or inside? ramp in, plunge in? finishing cut? tabs?
Pocket: ramp in, plunge in? finishing cut?


Deps
------

pysvg : does it buy me anything? svg parsing? do I need this? doesn't support inkscape specific things
svg.path : can evaluate bezier points [needed for interpolation]
affine : evaluation of transforms

What I need is:
- parser (read in svg from file or stdin)
- path/shape evaluator (transforms, points on line, center)
- style evaluator (to get cut parameters)
- writer (to gcode [text] or svg [to return to inkscape]?)
- options evaluator [read in tool/options from command line and document]
- style evaluator [css parser/resolver, what about xsl?]

for now use svg.path, affine, lxml (etree)



SVG -> moves in common format -> gcode

SVG parse paths to paths in common format
Paths in common format (with operations) to more complex paths
Convert common format paths to gcode


Common format
------
line to
arc to [G2 full circle is NOT supported in grbl, just do offsets, don't do radius mode]
curve to
