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

# NOTE: bl_info removed - blender_manifest.toml is the single source of
# metadata for Blender 4.2+ extensions.

import bpy
from . import float_curve_tools
from . import curve_profile_tools
from . import float_curve_export

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
