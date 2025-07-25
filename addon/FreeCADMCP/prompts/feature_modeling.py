"""
Prompt for feature-based modeling in FreeCAD
"""

def feature_modeling_guide() -> str:
    """Guide for creating features like fillets, chamfers, etc. in FreeCAD"""
    return """
Taiyaki AI - Feature-Based Modeling in FreeCAD

Feature-based modeling creates complex parts by adding features like fillets, chamfers, and shells to base shapes.
These operations modify existing geometry to add engineering features.

1. FILLETS (Rounding edges)
   - Creates a rounded transition between faces meeting at an edge
   - Parameters: edge selection, radius
   - Python code:
     ```python
     fillet = doc.addObject("Part::Fillet", "Fillet")
     fillet.Base = object
     fillet.Edges = [(edge_index, radius), ...]  # List of edge indices and radii
     doc.recompute()
     ```
   - Alternative using execute_code (easier with direct edge selection):
     ```python
     import Part
     obj = doc.getObject("ObjectName")
     edges = [obj.Shape.Edges[0], obj.Shape.Edges[2]]  # Select edges by index
     filleted = obj.Shape.makeFillet(radius, edges)
     result = doc.addObject("Part::Feature", "Filleted")
     result.Shape = filleted
     doc.recompute()
     ```

2. CHAMFERS (Beveled edges)
   - Creates an angled transition between faces
   - Parameters: edge selection, distance
   - Python code (similar to fillets):
     ```python
     chamfer = doc.addObject("Part::Chamfer", "Chamfer")
     chamfer.Base = object
     chamfer.Edges = [(edge_index, distance), ...]  # List of edge indices and distances
     doc.recompute()
     ```

3. SHELLS (Hollow objects)
   - Creates a hollow shell with specified thickness
   - Parameters: object, thickness, faces to remove
   - Python code:
     ```python
     shell = doc.addObject("Part::Thickness", "Shell")
     shell.Faces = face_indices  # List of face indices to remove (for openings)
     shell.Value = thickness      # Wall thickness (negative for inward, positive for outward)
     shell.Base = object
     doc.recompute()
     ```

4. DRAFT (Angular taper)
   - Creates an angled taper on a face
   - Parameters: face, pull direction, angle
   - Typically done through PartDesign but can be scripted

BEST PRACTICES:
- Apply fillets and chamfers last in your modeling sequence
- Start with small fillets and increase if needed
- For complex parts, apply fillets in groups rather than all at once
- Consider symmetry when applying features
- When creating shells, ensure the thickness is appropriate for manufacturing

EXAMPLE - Creating a filleted box:
```python
# Create a box
box = doc.addObject("Part::Box", "Box")
box.Length = 20
box.Width = 20
box.Height = 10
doc.recompute()

# Apply fillets to all vertical edges
import Part
edges = [box.Shape.Edges[i] for i in [0, 2, 5, 7]]  # Vertical edges
filleted = box.Shape.makeFillet(2.0, edges)
fillet_obj = doc.addObject("Part::Feature", "FilletedBox")
fillet_obj.Shape = filleted
doc.recompute()
```
"""