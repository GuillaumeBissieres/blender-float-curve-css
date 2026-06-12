# blender-float-curve-css

<img width="1200" height="600" alt="Column_Gen" src="https://github.com/user-attachments/assets/d9c06f22-cf05-4986-8ee6-b9a522f459c2" />

#

Float Curve CSS is a Blender add-on that enables the extraction, conversion, and reapplication of Float Curve data. It transforms curve profiles into normalized Float Curves using point simplification. Users can select any Float Curve node, such as those used in Geometry Nodes or shading setups, and copy the data directly to the clipboard formatted as CSS.

The tool natively supports generating either linear() functions or sampled values. Beyond exporting, Curve CSS allows users to reset Float Curves or paste previously saved curve data back into new or existing nodes. This enables consistent easing patterns and curve shapes to be transferred between different parts of a project or across entirely different Blender sessions.

# Installation
Download the ZIP file.

Open Blender and go to **Edit** > **Preferences** > **Add-ons**.

Click **Install**, select the ZIP file, and click **Install Add-on**.

Enable the add-on by checking the corresponding box.

Access **Float Curve Tools** in the **N menu** (sidebar) under the **Float Curve**.

# How to Use Float Curve Tools (Node Editor)
1. **Select a Float Curve node** in the Geometry Nodes editor.
2. **Choose the action**:
   - **Copy Curve** : Copies all points of the active Float Curve node. 
     Use Apply Curve afterwards to paste them onto any other Float Curve node.
   - **Apply Curve** : Pastes the previously copied curve points onto the 
     currently active Float Curve node. Select the target node first, 
     then click Apply.
   - **Apply From Text** : Apply curve points from a JSON text field directly 
     onto the active Float Curve node.
   - **Stretch X / Y** : Stretches the curve along the X or Y axis using a 
     slider. Adjusts in real time.
   - **Redistribute** : Evenly redistributes the inner control points along 
     the curve domain using a blend slider.

# How to Use Curve Profile (3D Viewport)
1. **Create or edit a Curve object** in the 3D Viewport to define the 
   desired profile shape.
2. **Register the Curve** : Click **Register Curve Profile** to add it to 
   the list.
3. **Create / Update Float Curve** : Converts the registered Curve Profile 
   into a Float Curve node inside the active object's Geometry Nodes 
   modifier. The modifier and node are created automatically if they do 
   not exist yet.
4. **Orientation options** :
   - **Flip Vertical** : Flips the curve profile values upside down before 
     applying to the Float Curve node.
   - **Flip Horizontal** : Mirrors the curve profile left to right before 
     applying to the Float Curve node.

# Advanced Options
- **Simplification** : Uses the Ramer–Douglas–Peucker algorithm to reduce 
  the number of control points while preserving the curve shape.
- **Precision** : Controls the number of sample points per Bezier segment 
  for accurate curve conversion.
- **Smart Handle Detection** : Automatically assigns VECTOR handles at peaks 
  and valleys and AUTO handles elsewhere for natural curve interpolation.
