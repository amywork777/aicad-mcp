"""
Prompt for pattern generation in FreeCAD
"""

def pattern_generation_guide() -> str:
    """Guide for creating patterns and arrays in FreeCAD"""
    return """
Taiyaki AI - Pattern Generation in FreeCAD

Patterns allow you to create arrays of objects in various configurations. 
FreeCAD provides several pattern tools that can be accessed via Python.

1. RECTANGULAR ARRAY
   - Creates a grid pattern of objects
   - Parameters: X direction, Y direction, X count, Y count
   - Perfect for creating grid-like patterns
   - Python code (Draft workbench):
     ```python
     import Draft
     rect_array = Draft.make_rectangular_array(
         object,
         FreeCAD.Vector(x_spacing, 0, 0),   # X direction
         FreeCAD.Vector(0, y_spacing, 0),   # Y direction
         x_count,                          # X count
         y_count                           # Y count
     )
     ```

2. POLAR ARRAY
   - Creates a circular pattern of objects
   - Parameters: center point, angle, count
   - Ideal for radial arrangements like gear teeth, spokes, etc.
   - Python code (Draft workbench):
     ```python
     import Draft
     polar_array = Draft.make_polar_array(
         object,
         FreeCAD.Vector(0, 0, 1),     # Axis
         360.0,                       # Angle (full circle)
         count,                       # Number of copies
         radius                       # Radius of the circle
     )
     ```

3. MIRROR
   - Creates a mirrored copy of an object
   - Parameters: mirror plane (defined by a base point and normal)
   - Useful for symmetrical designs
   - Python code:
     ```python
     import Draft
     mirror = Draft.make_mirror(
         object,
         FreeCAD.Vector(0, 0, 0),    # Base point
         FreeCAD.Vector(1, 0, 0)     # Normal (X axis)
     )
     ```

BEST PRACTICES:
- When creating arrays, group objects first for better organization
- For circular patterns, ensure the center and radius are appropriate
- Name the resulting array clearly (e.g., "BoltPattern" or "HoleArray")
- Consider using the PartDesign workbench for patterns within a part

EXAMPLE - Creating a bolt pattern:
```python
# Create a single bolt
bolt = doc.addObject("Part::Cylinder", "Bolt")
bolt.Radius = 2
bolt.Height = 10

# Create a circular pattern of bolts
import Draft
bolt_pattern = Draft.make_polar_array(
    bolt,
    FreeCAD.Vector(0, 0, 1),    # Z axis
    360.0,                      # Full circle
    8,                         # 8 bolts
    50                         # At 50mm radius
)
bolt_pattern.Label = "BoltPattern"
doc.recompute()
```
"""