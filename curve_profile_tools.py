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
# Curve Profile Tools - View3D
# =====================================================

import bpy
import json
from mathutils import Vector
from bpy.props import (
    CollectionProperty,
    PointerProperty,
    StringProperty,
    IntProperty,
    FloatProperty,
    BoolProperty,
)

# =====================================================
# DATA
# =====================================================
class CBP_Profile(bpy.types.PropertyGroup):
    name: StringProperty()
    curve_obj: PointerProperty(type=bpy.types.Object)
    css_text: StringProperty(default="")

# =====================================================
# CURVE EXTRACTION
# =====================================================
def extract_curve_points(obj, precision=32):
    pts = []
    for spline in obj.data.splines:
        if spline.type == 'BEZIER':
            bps = spline.bezier_points
            for i in range(len(bps) - 1):
                p0 = bps[i].co
                h0 = bps[i].handle_right
                h1 = bps[i + 1].handle_left
                p1 = bps[i + 1].co
                for s in range(precision + 1):
                    t = s / precision
                    it = 1.0 - t
                    co = (
                        it**3 * p0 +
                        3 * it**2 * t * h0 +
                        3 * it * t**2 * h1 +
                        t**3 * p1
                    )
                    pts.append(Vector((co.x, co.y)))
        else:
            for p in spline.points:
                pts.append(Vector((p.co.x, p.co.y)))
    return pts

# =====================================================
# PROJECTION
# =====================================================
def project_profile(points, flip_vertical=False, flip_horizontal=False):
    if len(points) < 2:
        return points

    arc_lengths = [0.0]
    total_length = 0.0
    for i in range(1, len(points)):
        seg = (points[i] - points[i - 1]).length
        total_length += seg
        arc_lengths.append(total_length)

    if total_length == 0:
        return [Vector((0, 0)), Vector((1, 1))]

    min_x = min(p.x for p in points)
    max_x = max(p.x for p in points)
    min_y = min(p.y for p in points)
    max_y = max(p.y for p in points)

    width = max_x - min_x
    height = max_y - min_y

    if width >= height:
        values = [p.y for p in points]
        min_val, max_val = min_y, max_y
    else:
        values = [p.x for p in points]
        min_val, max_val = min_x, max_x

    val_range = max(max_val - min_val, 1e-5)

    normalized = []
    for i, val in enumerate(values):
        x = arc_lengths[i] / total_length
        y = (val - min_val) / val_range
        if flip_horizontal:
            x = 1.0 - x
        if flip_vertical:
            y = 1.0 - y
        normalized.append(Vector((x, y)))

    if flip_horizontal:
        normalized.reverse()

    return normalized

# =====================================================
# SIMPLIFICATION
# =====================================================
def simplify_curve_rdp(points, epsilon=0.005):
    if len(points) <= 2:
        return points

    dmax = 0.0
    index = 0
    end = len(points) - 1

    for i in range(1, end):
        d = perpendicular_distance(points[i], points[0], points[end])
        if d > dmax:
            dmax = d
            index = i

    if dmax > epsilon:
        r1 = simplify_curve_rdp(points[:index + 1], epsilon)
        r2 = simplify_curve_rdp(points[index:], epsilon)
        return r1[:-1] + r2
    else:
        return [points[0], points[end]]

def perpendicular_distance(p, a, b):
    if a == b:
        return (p - a).length
    ab = b - a
    ap = p - a
    t = ap.dot(ab.normalized())
    if t < 0:
        return (p - a).length
    if t > ab.length:
        return (p - b).length
    proj = a + ab.normalized() * t
    return (p - proj).length

# =====================================================
# FLOAT CURVE NODE FIND / CREATE  (RESTORED)
# =====================================================
def find_or_create_float_curve_node():
    obj = bpy.context.active_object

    if obj:
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group:
                for n in mod.node_group.nodes:
                    if hasattr(n, "mapping"):
                        return n

    ng = bpy.data.node_groups.get("CBP_FloatCurve_GN")
    if not ng:
        ng = bpy.data.node_groups.new("CBP_FloatCurve_GN", 'GeometryNodeTree')

    node = ng.nodes.new("ShaderNodeFloatCurve")
    node.location = (0, 0)
    return node

# =====================================================
# FLOAT CURVE APPLICATION (PEAK FIX ONLY)
# =====================================================
def apply_css(mapping, data):
    curve = mapping.curves[0]

    while len(curve.points) > 2:
        curve.points.remove(curve.points[-1])

    if len(curve.points) < 2:
        curve.points.new(0, 0)
        curve.points.new(1, 1)

    curve.points[0].location = (data[0].x, data[0].y)
    curve.points[-1].location = (data[-1].x, data[-1].y)
    curve.points[0].handle_type = 'AUTO'
    curve.points[-1].handle_type = 'AUTO'

    for i, d in enumerate(data[1:-1], start=1):
        p = curve.points.new(d.x, d.y)

        prev_y = data[i - 1].y
        curr_y = d.y
        next_y = data[i + 1].y

        is_peak = (curr_y > prev_y and curr_y > next_y)
        is_valley = (curr_y < prev_y and curr_y < next_y)

        p.handle_type = 'VECTOR' if (is_peak or is_valley) else 'AUTO'

    mapping.update()

# =====================================================
# OPERATORS
# =====================================================
class CBP_OT_register_curve(bpy.types.Operator):
    bl_idname = "cbp.register_curve"
    bl_label = "Register Curve Profile"

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'CURVE':
            self.report({'ERROR'}, "Select a Curve")
            return {'CANCELLED'}

        p = context.scene.cbp_profiles.add()
        p.name = obj.name
        p.curve_obj = obj
        context.scene.cbp_index = len(context.scene.cbp_profiles) - 1
        return {'FINISHED'}

class CBP_OT_delete_curve(bpy.types.Operator):
    bl_idname = "cbp.delete_curve"
    bl_label = "Delete Selected Profile"
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = context.scene
        if not scn.cbp_profiles:
            return {'CANCELLED'}

        idx = scn.cbp_index
        if idx < 0 or idx >= len(scn.cbp_profiles):
            return {'CANCELLED'}

        scn.cbp_profiles.remove(idx)
        scn.cbp_index = min(max(0, idx - 1), len(scn.cbp_profiles) - 1)
        return {'FINISHED'}

class CBP_OT_update_float_curve(bpy.types.Operator):
    bl_idname = "cbp.update_float_curve"
    bl_label = "Create / Update Float Curve"

    precision: IntProperty(default=32, min=8, max=128)
    simplify_epsilon: FloatProperty(default=0.005, min=0.0001, max=0.1)

    def execute(self, context):
        prof = context.scene.cbp_profiles[context.scene.cbp_index]
        scn = context.scene

        raw = extract_curve_points(prof.curve_obj, self.precision)
        proj = project_profile(raw, scn.cbp_flip_v, scn.cbp_flip_h)
        simp = simplify_curve_rdp(proj, self.simplify_epsilon)

        css = []
        for i, p in enumerate(simp):
            if 0 < i < len(simp) - 1:
                prev_y = simp[i - 1].y
                curr_y = p.y
                next_y = simp[i + 1].y
                sharp = (curr_y > prev_y and curr_y > next_y) or (curr_y < prev_y and curr_y < next_y)
                handle = "VECTOR" if sharp else "AUTO"
            else:
                handle = "AUTO"

            css.append({
                "x": round(p.x, 4),
                "y": round(p.y, 4),
                "type": handle
            })

        prof.css_text = json.dumps(css, separators=(',', ':'))

        node = find_or_create_float_curve_node()
        apply_css(node.mapping, simp)
        return {'FINISHED'}

# =====================================================
# UI (UNCHANGED)
# =====================================================
class VIEW3D_PT_curve_profile_tools(bpy.types.Panel):
    bl_label = "Curve Profile"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Curve Profile"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        row = layout.row(align=True)
        row.operator("cbp.register_curve", text="Register Curve Profile", icon='ADD')
        row.operator("cbp.delete_curve", text="", icon='TRASH')

        layout.template_list(
            "UI_UL_list", "CBP_LIST",
            scn, "cbp_profiles",
            scn, "cbp_index"
        )

        if scn.cbp_profiles:
            layout.operator("cbp.update_float_curve", icon='FCURVE')

            layout.separator()
            layout.label(text="Orientation:")
            row = layout.row(align=True)
            row.prop(scn, "cbp_flip_v", text="Flip Vertical", toggle=True)
            row.prop(scn, "cbp_flip_h", text="Flip Horizontal", toggle=True)

            layout.separator()
            layout.label(text="Float Curve CSS:")
            layout.prop(scn.cbp_profiles[scn.cbp_index], "css_text", text="")

# =====================================================
# REGISTER
# =====================================================
classes = (
    CBP_Profile,
    CBP_OT_register_curve,
    CBP_OT_delete_curve,
    CBP_OT_update_float_curve,
    VIEW3D_PT_curve_profile_tools,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.cbp_profiles = CollectionProperty(type=CBP_Profile)
    bpy.types.Scene.cbp_index = IntProperty()
    bpy.types.Scene.cbp_flip_v = BoolProperty(default=False)
    bpy.types.Scene.cbp_flip_h = BoolProperty(default=False)

def unregister():
    del bpy.types.Scene.cbp_flip_h
    del bpy.types.Scene.cbp_flip_v
    del bpy.types.Scene.cbp_profiles
    del bpy.types.Scene.cbp_index

    for c in reversed(classes):
        bpy.utils.unregister_class(c)
