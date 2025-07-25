"""
Prompt for boolean operations in FreeCAD
"""

def boolean_operations_guide() -> str:
    """Guide for using boolean operations in FreeCAD"""
    return """
Taiyaki AI - Boolean Operations in FreeCAD

Boolean operations are fundamental for creating complex shapes by combining simpler ones. 
FreeCAD supports three primary boolean operations through the Part workbench:

1. UNION (Fusion)
   - Combines two or more shapes into a single shape
   - Use when you want to join objects together
   - Python code:
     ```python
     fusion = doc.addObject("Part::Fusion", "Fusion")
     fusion.Base = object1
     fusion.Tool = object2
     doc.recompute()
     ```

2. DIFFERENCE (Cut)
   - Subtracts one shape from another
   - Use when creating holes, cutouts, or removing material
   - Python code:
     ```python
     cut = doc.addObject("Part::Cut", "Cut")
     cut.Base = object1  # The object to cut from
     cut.Tool = object2  # The cutting tool
     doc.recompute()
     ```

3. INTERSECTION (Common)
   - Creates a shape from the volume common to both shapes
   - Use when you want only the overlapping portion
   - Python code:
     ```python
     common = doc.addObject("Part::Common", "Common")
     common.Base = object1
     common.Tool = object2
     doc.recompute()
     ```

BEST PRACTICES:
- Always name the result with a descriptive name that indicates what the operation does
- For complex operations, perform boolean operations in steps rather than all at once
- If a boolean operation fails, check for:
  * Non-solid objects (must be solid)
  * Zero-thickness faces
  * Self-intersecting geometry
  * Coincident faces

EXAMPLE - Creating a hole in a box:
```python
# Create a box
box = doc.addObject("Part::Box", "Box")
box.Length = 20
box.Width = 20
box.Height = 10

# Create a cylinder for the hole
cylinder = doc.addObject("Part::Cylinder", "Hole")
cylinder.Radius = 5
cylinder.Height = 15
cylinder.Placement.Base = FreeCAD.Vector(10, 10, -2.5)

# Subtract the cylinder from the box
cut = doc.addObject("Part::Cut", "BoxWithHole")
cut.Base = box
cut.Tool = cylinder
doc.recompute()
```
"""