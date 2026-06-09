# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# =====================================================
# Float Curve Tools
# =====================================================
# Unified addon:
# - Float Curve Tools (Node Editor)
# - Curve Profile Tools (View3D)
# - Float Curve Export (Node Editor → Curve Object)
#
# Author: Guillaume Bissieres
# =====================================================

bl_info = {
    "name": "Float Curve Tools",
    "author": "Guillaume Bissieres",
    "version": (1, 2, 0),
    "blender": (4, 5, 0),
    "location": "Node Editor > Sidebar | View3D > Sidebar",
    "description": (
        "Advanced Float Curve editing tools (copy / paste, flip, stretch, "
        "domain mirror, proper point redistribution) combined with smart "
        "Curve Profile to Float Curve conversion and Float Curve to Curve export."
    ),
    "doc_url": "https://bissieres.gumroad.com/l/CurveCss",
    "tracker_url": "https://github.com/GuillaumeBissieres/blender-float-curve-css",
    "category": "Node",
}

import bpy

# -----------------------------------------------------
# Import submodules
# -----------------------------------------------------
from . import float_curve_tools
from . import curve_profile_tools
from . import float_curve_export


# =====================================================
# REGISTER
# =====================================================

def register():
    float_curve_tools.register()
    curve_profile_tools.register()
    float_curve_export.register()


def unregister():
    float_curve_export.unregister()
    curve_profile_tools.unregister()
    float_curve_tools.unregister()


if __name__ == "__main__":
    register()
