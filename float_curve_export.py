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
# Float Curve Export
# Export active Float Curve node to a Bezier Curve object
# ==========================================================

import bpy


class NODE_OT_export_float_curve_to_curve(bpy.types.Operator):
    """Export the active Float Curve node to a Bezier Curve object"""
    bl_idname = "node.export_float_curve_to_curve"
    bl_label = "Export Float Curve To Curve"
    bl_description = (
        "Export the active Float Curve node to a Bezier Curve object "
        "in the 3D Viewport, preserving shape, points, and sharp peaks"
    )
    bl_options = {'REGISTER', 'UNDO'}

    scale_x: bpy.props.FloatProperty(
        name="Scale X",
        description="Scale of the curve on X axis",
        default=1.0,
        min=0.0001
    )

    scale_y: bpy.props.FloatProperty(
        name="Scale Y",
        description="Scale of the curve on Y axis",
        default=1.0,
        min=0.0001
    )

    @classmethod
    def poll(cls, context):
        node = getattr(context, "active_node", None)
        return node is not None and hasattr(node, "mapping")

    def execute(self, context):
        node = context.active_node

        fc_points = node.mapping.curves[0].points
        if len(fc_points) < 2:
            self.report({'ERROR'}, "Float Curve has not enough points")
            return {'CANCELLED'}

        curve_data = bpy.data.curves.new("FloatCurve_Export", type='CURVE')
        curve_data.dimensions = '3D'

        spline = curve_data.splines.new(type='BEZIER')
        spline.bezier_points.add(len(fc_points) - 1)

        for i, p in enumerate(fc_points):
            bp = spline.bezier_points[i]

            x = p.location.x * self.scale_x
            z = p.location.y * self.scale_y
            bp.co = (x, 0.0, z)

            if 0 < i < len(fc_points) - 1:
                prev_y = fc_points[i - 1].location.y
                curr_y = p.location.y
                next_y = fc_points[i + 1].location.y

                is_peak = (curr_y > prev_y and curr_y > next_y)
                is_valley = (curr_y < prev_y and curr_y < next_y)

                if is_peak or is_valley:
                    bp.handle_left_type = 'VECTOR'
                    bp.handle_right_type = 'VECTOR'
                    continue

            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'

        obj = bpy.data.objects.new("FloatCurve_Export", curve_data)
        context.collection.objects.link(obj)
        obj.location = context.scene.cursor.location

        self.report({'INFO'}, "Float Curve exported correctly")
        return {'FINISHED'}


class NODE_PT_float_curve_export(bpy.types.Panel):
    bl_label = "Float Curve Export"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Float Curve"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Export active Float Curve:")
        layout.operator(
            "node.export_float_curve_to_curve",
            icon='CURVE_BEZCURVE'
        )


classes = (
    NODE_OT_export_float_curve_to_curve,
    NODE_PT_float_curve_export,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
