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

# ==========================================================
# Float Curve Tools - Node Editor
# (bl_info intentionally removed, handled by __init__.py)
# ==========================================================

import bpy
import json
import ast

STORED_POINTS = []
ORIGINAL_POINTS = []

# ==========================================================
# NODE SEARCH
# ==========================================================
def find_selected_float_curve_node():
    space = bpy.context.space_data
    if space and space.type == 'NODE_EDITOR' and space.node_tree:
        for n in space.node_tree.nodes:
            if n.select and hasattr(n, "mapping"):
                return n
        if space.node_tree.nodes.active and hasattr(space.node_tree.nodes.active, "mapping"):
            return space.node_tree.nodes.active

    for ng in bpy.data.node_groups:
        if ng.nodes.active and hasattr(ng.nodes.active, "mapping"):
            return ng.nodes.active

    return None

# ==========================================================
# CURVE UTILS
# ==========================================================
def extract_curve_points(mapping):
    curve = mapping.curves[0]
    return [{
        "x": float(p.location[0]),
        "y": float(p.location[1]),
        "type": getattr(p, "handle_type", "FREE")
    } for p in curve.points]

def apply_curve_points(mapping, data):
    curve = mapping.curves[0]

    while len(curve.points) > 2:
        curve.points.remove(curve.points[-1])

    if len(curve.points) < 2:
        curve.points.new(data[0]["x"], data[0]["y"])
        curve.points.new(data[-1]["x"], data[-1]["y"])

    curve.points[0].location = (data[0]["x"], data[0]["y"])
    curve.points[0].handle_type = data[0]["type"]

    curve.points[1].location = (data[-1]["x"], data[-1]["y"])
    curve.points[1].handle_type = data[-1]["type"]

    for d in data[1:-1]:
        p = curve.points.new(d["x"], d["y"])
        p.handle_type = d.get("type", "FREE")

    mapping.update()

# ==========================================================
# TRANSFORMS
# ==========================================================
def flip_curve(mapping, mode):
    global ORIGINAL_POINTS
    data = extract_curve_points(mapping)
    ORIGINAL_POINTS = data.copy()

    flipped = []
    for p in data:
        x, y = p["x"], p["y"]
        if mode == 'HORIZONTAL':
            x = 1.0 - x
        elif mode == 'VERTICAL':
            y = 1.0 - y
        flipped.append({"x": x, "y": y, "type": p["type"]})

    apply_curve_points(mapping, flipped)
    ORIGINAL_POINTS = flipped.copy()

def stretch_curve(mapping, scale_x=1.0, scale_y=1.0):
    global ORIGINAL_POINTS
    if not ORIGINAL_POINTS:
        ORIGINAL_POINTS = extract_curve_points(mapping)

    cx, cy = 0.5, 0.5
    stretched = []

    for p in ORIGINAL_POINTS:
        stretched.append({
            "x": cx + (p["x"] - cx) * scale_x,
            "y": cy + (p["y"] - cy) * scale_y,
            "type": p["type"]
        })

    apply_curve_points(mapping, stretched)

def flip_curve_domain_x(mapping):
    data = extract_curve_points(mapping)

    mirrored = []
    for p in reversed(data):
        mirrored.append({
            "x": 1.0 - p["x"],
            "y": p["y"],
            "type": p["type"]
        })

    apply_curve_points(mapping, mirrored)

# ==========================================================
# TRUE POINT REDISTRIBUTION
# ==========================================================
def redistribute_curve_points(mapping, factor=0.0):
    global ORIGINAL_POINTS

    if not ORIGINAL_POINTS:
        ORIGINAL_POINTS = extract_curve_points(mapping)

    pts = ORIGINAL_POINTS
    count = len(pts)

    if count < 3:
        return

    min_x = pts[0]["x"]
    max_x = pts[-1]["x"]
    length = max_x - min_x

    if length == 0:
        return

    inner_count = count - 2
    uniform_x = [
        min_x + (i + 1) * length / (inner_count + 1)
        for i in range(inner_count)
    ]

    redistributed = [pts[0]]

    for i in range(inner_count):
        p = pts[i + 1]
        target_x = uniform_x[i]
        x = p["x"] * (1.0 - factor) + target_x * factor
        redistributed.append({
            "x": x,
            "y": p["y"],
            "type": p["type"]
        })

    redistributed.append(pts[-1])
    apply_curve_points(mapping, redistributed)

# ==========================================================
# UPDATE CALLBACKS
# ==========================================================
def update_curve_stretch(self, context):
    node = find_selected_float_curve_node()
    if node:
        stretch_curve(
            node.mapping,
            context.scene.float_curve_stretch_x,
            context.scene.float_curve_stretch_y
        )

def update_curve_redistribute(self, context):
    node = find_selected_float_curve_node()
    if node:
        redistribute_curve_points(
            node.mapping,
            context.scene.float_curve_redistribute
        )

# ==========================================================
# OPERATORS
# ==========================================================
class NODE_OT_copy_float_curve_points(bpy.types.Operator):
    bl_idname = "node.copy_float_curve_points"
    bl_label = "Copy Curve"

    def execute(self, context):
        global STORED_POINTS, ORIGINAL_POINTS
        node = find_selected_float_curve_node()
        if not node:
            return {'CANCELLED'}

        STORED_POINTS = extract_curve_points(node.mapping)
        ORIGINAL_POINTS = STORED_POINTS.copy()

        context.scene.float_curve_tools_text = json.dumps(STORED_POINTS)
        context.scene.float_curve_stretch_x = 1.0
        context.scene.float_curve_stretch_y = 1.0
        context.scene.float_curve_redistribute = 0.0

        return {'FINISHED'}

class NODE_OT_apply_float_curve_points(bpy.types.Operator):
    bl_idname = "node.apply_float_curve_points"
    bl_label = "Apply Curve"

    def execute(self, context):
        node = find_selected_float_curve_node()
        if node and STORED_POINTS:
            apply_curve_points(node.mapping, STORED_POINTS)
        return {'FINISHED'}

class NODE_OT_apply_from_text(bpy.types.Operator):
    bl_idname = "node.apply_float_curve_from_text"
    bl_label = "Apply From Text"

    def execute(self, context):
        try:
            data = ast.literal_eval(context.scene.float_curve_tools_text)
        except Exception:
            return {'CANCELLED'}

        node = find_selected_float_curve_node()
        if node:
            apply_curve_points(node.mapping, data)
        return {'FINISHED'}

class NODE_OT_flip_curve_vertical(bpy.types.Operator):
    bl_idname = "node.flip_float_curve_vertical"
    bl_label = "Flip Vertical"

    def execute(self, context):
        node = find_selected_float_curve_node()
        if node:
            flip_curve(node.mapping, 'VERTICAL')
        return {'FINISHED'}

class NODE_OT_flip_curve_horizontal(bpy.types.Operator):
    bl_idname = "node.flip_float_curve_horizontal"
    bl_label = "Flip Horizontal"

    def execute(self, context):
        node = find_selected_float_curve_node()
        if node:
            flip_curve(node.mapping, 'HORIZONTAL')
        return {'FINISHED'}

class NODE_OT_flip_curve_domain_x(bpy.types.Operator):
    bl_idname = "node.flip_float_curve_domain_x"
    bl_label = "Flip Domain (Visual)"

    def execute(self, context):
        node = find_selected_float_curve_node()
        if node:
            flip_curve_domain_x(node.mapping)
        return {'FINISHED'}

# ==========================================================
# UI
# ==========================================================
class NODE_PT_float_curve_css(bpy.types.Panel):
    bl_idname = "NODE_PT_float_curve_css"
    bl_label = "Float Curve Tools"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Float Curve"

    def draw(self, context):
        layout = self.layout

        layout.operator("node.copy_float_curve_points", icon='COPYDOWN')
        layout.operator("node.apply_float_curve_points", icon='PASTEDOWN')

        layout.separator()
        layout.label(text="Points:")
        row = layout.row(align=True)
        row.operator("node.flip_float_curve_vertical")
        row.operator("node.flip_float_curve_horizontal")

        layout.operator("node.flip_float_curve_domain_x", icon='ARROW_LEFTRIGHT')

        layout.separator()
        layout.label(text="Stretch:")
        layout.prop(context.scene, "float_curve_stretch_x", slider=True)
        layout.prop(context.scene, "float_curve_stretch_y", slider=True)

        layout.separator()
        layout.label(text="Redistribute:")
        layout.prop(context.scene, "float_curve_redistribute", slider=True)

        layout.separator()
        layout.label(text="Curve data:")
        layout.prop(context.scene, "float_curve_tools_text", text="")
        layout.operator("node.apply_float_curve_from_text", icon='FILE_TICK')

# ==========================================================
# REGISTER
# ==========================================================
classes = (
    NODE_OT_copy_float_curve_points,
    NODE_OT_apply_float_curve_points,
    NODE_OT_apply_from_text,
    NODE_OT_flip_curve_vertical,
    NODE_OT_flip_curve_horizontal,
    NODE_OT_flip_curve_domain_x,
    NODE_PT_float_curve_css,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.float_curve_tools_text = bpy.props.StringProperty(default="")
    bpy.types.Scene.float_curve_stretch_x = bpy.props.FloatProperty(
        default=1.0, min=0.01, max=5.0, update=update_curve_stretch
    )
    bpy.types.Scene.float_curve_stretch_y = bpy.props.FloatProperty(
        default=1.0, min=0.01, max=5.0, update=update_curve_stretch
    )
    bpy.types.Scene.float_curve_redistribute = bpy.props.FloatProperty(
        default=0.0, min=0.0, max=1.0, update=update_curve_redistribute
    )

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.float_curve_tools_text
    del bpy.types.Scene.float_curve_stretch_x
    del bpy.types.Scene.float_curve_stretch_y
    del bpy.types.Scene.float_curve_redistribute
