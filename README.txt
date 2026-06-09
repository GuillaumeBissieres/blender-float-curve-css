Float Curve Tools

Float Curve Tools is a unified Blender add-on that provides advanced tools for editing Float Curves and converting Curve Profiles into optimized Float Curves.

It combines two previously separate tools into a single, clean add-on, without changing any workflow or UI location.

--------------------------------------------------
FEATURES OVERVIEW
--------------------------------------------------

1. Float Curve Editing (Node Editor)

- Copy / Paste Float Curve points
- Flip curve vertically or horizontally
- Flip curve domain (visual mirror)
- Stretch curve on X and Y axes
- Proper point redistribution (Graph Editor style)
- Import / export curve data as text (CSS-like format)

2. Curve Profile to Float Curve Conversion (View3D)

- Register multiple Curve Profiles
- Smart projection and normalization
- Automatic orientation detection
- Optional horizontal / vertical flip
- Curve simplification (RDP algorithm)
- Automatic Float Curve node creation / update

--------------------------------------------------
INSTALLATION
--------------------------------------------------

1. Download the add-on ZIP file
2. In Blender:
   - Edit > Preferences > Add-ons > Install
   - Select the ZIP file
3. Enable "Float Curve Tools"

Compatible with Blender 4.5+

--------------------------------------------------
UI LOCATIONS
--------------------------------------------------

Float Curve Tools:
- Node Editor
- Sidebar (N key)
- Tab: Float Curve

Curve Profile Tools:
- 3D Viewport
- Sidebar (N key)
- Tab: Curve Profile

--------------------------------------------------
FLOAT CURVE TOOLS - USAGE
--------------------------------------------------

Copy Curve:
Copies all points of the selected Float Curve.

Apply Curve:
Applies the copied curve to the active Float Curve node.

Apply From Text:
Applies curve data pasted into the text field.

Flip Vertical:
Mirrors the curve on the Y axis.

Flip Horizontal:
Mirrors the curve on the X axis.

Flip Domain (Visual):
Reverses the curve domain while preserving its visual shape.

Stretch:
- Stretch X scales horizontally
- Stretch Y scales vertically
Operations are centered and non-destructive.

Redistribute:
Redistributes inner points evenly along the X axis
from original to fully uniform.

--------------------------------------------------
CURVE PROFILE TOOLS - USAGE
--------------------------------------------------

Register Curve Profile:
Select a Curve object and register it in the list.

Create / Update Float Curve:
Extracts the curve shape, normalizes it,
simplifies it, and creates or updates a Float Curve node.

Orientation:
- Flip Vertical: invert values
- Flip Horizontal: reverse direction

Float Curve CSS Field:
Displays generated Float Curve data for reuse.

--------------------------------------------------
TECHNICAL NOTES
--------------------------------------------------

- Non-destructive workflow
- No modifiers added automatically
- Compatible with Geometry Nodes and Shader Nodes

--------------------------------------------------
AUTHOR
--------------------------------------------------

Guillaume Bissieres
https://bissieres.gumroad.com/l/CurveCss

--------------------------------------------------
LICENSE
--------------------------------------------------

GNU General Public License v3 or later

--------------------------------------------------
VERSION
--------------------------------------------------

Float Curve Tools v1.1.0
