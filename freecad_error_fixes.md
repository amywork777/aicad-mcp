# FreeCAD Error Fixes and Troubleshooting Guide

## Common FreeCAD Wrench Design Errors and Solutions

### 1. Geometry Creation Errors

#### Error: "AttributeError: module has no attribute 'makeBox'"
**Cause**: Missing Part module import or incorrect syntax
**Solution**:
```python
import Part
box = Part.makeBox(length, width, height)  # Correct
# NOT: box = FreeCAD.makeBox(...)  # Wrong
```

#### Error: "TypeError: makePolygon() argument after * must be a sequence"
**Cause**: Incorrect polygon point format
**Solution**:
```python
# Correct way to create polygon
points = [FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0), ...]
points.append(points[0])  # Close the polygon
wire = Part.makePolygon(points)

# Alternative using list comprehension
hex_points = [FreeCAD.Vector(hex_size * math.cos(i * math.pi / 3), 
                            hex_size * math.sin(i * math.pi / 3), 0) 
              for i in range(6)]
hex_points.append(hex_points[0])  # Close
```

#### Error: "Part.OCCError: Standard_DomainError"
**Cause**: Invalid geometric operations (self-intersecting shapes, invalid cuts)
**Solution**:
```python
# Check shape validity before operations
if handle.Shape.isValid():
    result = handle.Shape.fuse(head.Shape)
else:
    print("Invalid handle shape - check dimensions")

# Ensure proper positioning before cuts
hex_hole.Placement.Base = FreeCAD.Vector(x, y, -0.1)  # Slight offset for clean cut
```

### 2. Fillet and Chamfer Errors

#### Error: "Part.OCCError: BRepFilletAPI_MakeFillet"
**Cause**: Trying to fillet edges that don't exist or are too small
**Solution**:
```python
# Filter edges properly
edges_to_fillet = []
for edge in shape.Edges:
    # Only fillet edges of appropriate length
    if 2.0 < edge.Length < 50.0:
        edges_to_fillet.append(edge)

# Try filleting with error handling
try:
    if edges_to_fillet:
        filleted_shape = shape.makeFillet(radius, edges_to_fillet[:4])  # Limit count
except:
    print("Warning: Filleting failed, continuing without fillets")
    filleted_shape = shape
```

### 3. TechDraw and PDF Export Errors

#### Error: "AttributeError: DrawPage has no attribute 'exportPdf'"
**Cause**: Incorrect TechDraw API usage or missing dependencies
**Solution**:
```python
# Method 1: Direct PDF export
try:
    page.exportPdf(output_path)
except AttributeError:
    # Fallback: Export as SVG first
    svg_path = output_path.replace('.pdf', '.svg')
    page.exportSvg(svg_path)
    print(f"Exported as SVG: {svg_path}")

# Method 2: Use Qt print functionality
try:
    import PySide2.QtPrintSupport as QtPrint
    printer = QtPrint.QPrinter()
    printer.setOutputFormat(QtPrint.QPrinter.PdfFormat)
    printer.setOutputFileName(output_path)
    page.print(printer)
except ImportError:
    print("Qt print support not available")
```

#### Error: "RuntimeError: No template found"
**Cause**: Missing template file
**Solution**:
```python
# Template search with fallbacks
template_paths = [
    "/usr/share/freecad/Mod/TechDraw/Templates/A4_LandscapeTD.svg",
    "/usr/share/freecad/data/Mod/TechDraw/Templates/A4_LandscapeTD.svg",
    "/snap/freecad/current/share/freecad/Mod/TechDraw/Templates/A4_LandscapeTD.svg",
    "/opt/freecad/Mod/TechDraw/Templates/A4_LandscapeTD.svg"
]

template_found = False
for template_path in template_paths:
    if os.path.exists(template_path):
        template.Template = template_path
        template_found = True
        break

if not template_found:
    # Create minimal custom template
    custom_template = '''<?xml version="1.0" encoding="UTF-8"?>
    <svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm">
      <rect width="297mm" height="210mm" fill="white" stroke="black"/>
      <text x="10mm" y="200mm">Technical Drawing</text>
    </svg>'''
    
    template_file = "/tmp/custom_template.svg"
    with open(template_file, 'w') as f:
        f.write(custom_template)
    template.Template = template_file
```

### 4. Document and Object Management Errors

#### Error: "RuntimeError: Cannot find object in document"
**Cause**: Object was deleted or document was closed
**Solution**:
```python
# Safe object creation with error checking
def safe_add_object(doc, obj_type, name):
    try:
        if name in [obj.Name for obj in doc.Objects]:
            doc.removeObject(name)  # Remove existing
        return doc.addObject(obj_type, name)
    except:
        # Generate unique name if conflicts
        import uuid
        unique_name = f"{name}_{uuid.uuid4().hex[:8]}"
        return doc.addObject(obj_type, unique_name)

# Document cleanup
def cleanup_document(doc_name):
    if doc_name in FreeCAD.listDocuments():
        try:
            FreeCAD.closeDocument(doc_name)
        except:
            pass  # Document already closed or doesn't exist
```

### 5. ViewObject and Visibility Errors

#### Error: "AttributeError: 'NoneType' object has no attribute 'ViewObject'"
**Cause**: Object creation failed but code continues
**Solution**:
```python
# Always check object creation success
handle = doc.addObject("Part::Feature", "Handle")
if handle and handle.Shape:
    handle.Shape = handle_box
    if hasattr(handle, 'ViewObject') and handle.ViewObject:
        handle.ViewObject.ShapeColor = (0.7, 0.7, 0.7)
        handle.ViewObject.Visibility = True
else:
    print("Error: Handle creation failed")
    return None
```

### 6. Import and Module Errors

#### Error: "ModuleNotFoundError: No module named 'FreeCAD'"
**Cause**: FreeCAD not installed or not in Python path
**Solution**:
```bash
# Install FreeCAD
sudo apt update
sudo apt install freecad

# For headless operation
sudo apt install freecad-python3

# Alternative: Install via snap
sudo snap install freecad

# Verify installation
python3 -c "import FreeCAD; print('FreeCAD version:', FreeCAD.Version())"
```

#### Error: "ImportError: cannot import name 'TechDraw'"
**Cause**: TechDraw workbench not available
**Solution**:
```python
# Conditional import with fallback
try:
    import TechDraw
    TECHDRAW_AVAILABLE = True
except ImportError:
    print("TechDraw not available, using alternative approach")
    TECHDRAW_AVAILABLE = False

# Alternative: Use Draft for 2D
if not TECHDRAW_AVAILABLE:
    import Draft
    # Create 2D projection using Draft tools
```

## Robust Wrench Design Template

```python
#!/usr/bin/env python3
"""
Robust FreeCAD Wrench Designer with comprehensive error handling
"""

import os
import sys
import math
import traceback

class RobustWrenchDesigner:
    def __init__(self):
        self.modules_loaded = False
        self.doc = None
        
    def load_modules(self):
        """Load FreeCAD modules with error handling"""
        try:
            import FreeCAD
            import Part
            self.FreeCAD = FreeCAD
            self.Part = Part
            
            # Optional modules
            try:
                import Draft
                self.Draft = Draft
            except ImportError:
                self.Draft = None
                
            try:
                import TechDraw
                self.TechDraw = TechDraw
            except ImportError:
                self.TechDraw = None
                
            self.modules_loaded = True
            return True
            
        except ImportError as e:
            print(f"Error loading FreeCAD: {e}")
            return False
    
    def create_safe_box(self, length, width, height, name="Box"):
        """Create box with error handling"""
        try:
            if length <= 0 or width <= 0 or height <= 0:
                raise ValueError("Box dimensions must be positive")
                
            box_shape = self.Part.makeBox(length, width, height)
            
            if not box_shape.isValid():
                raise RuntimeError("Created box is invalid")
                
            box_obj = self.doc.addObject("Part::Feature", name)
            box_obj.Shape = box_shape
            
            return box_obj
            
        except Exception as e:
            print(f"Error creating box {name}: {e}")
            return None
    
    def create_safe_hex_hole(self, center, size, thickness, name="HexHole"):
        """Create hexagonal hole with robust error handling"""
        try:
            radius = size / math.sqrt(3)  # Flat-to-flat to circumradius
            
            # Create hexagon points
            points = []
            for i in range(6):
                angle = i * math.pi / 3
                x = center[0]
                y = center[1] + radius * math.cos(angle)
                z = center[2] + radius * math.sin(angle)
                points.append(self.FreeCAD.Vector(x, y, z))
            
            # Close the polygon
            points.append(points[0])
            
            # Create wire and face
            wire = self.Part.makePolygon(points)
            if not wire.isValid():
                raise RuntimeError("Hex wire is invalid")
                
            face = self.Part.Face(wire)
            if not face.isValid():
                raise RuntimeError("Hex face is invalid")
            
            # Extrude
            extrude_vec = self.FreeCAD.Vector(0, 0, thickness + 1)
            hole_shape = face.extrude(extrude_vec)
            
            if not hole_shape.isValid():
                raise RuntimeError("Extruded hex hole is invalid")
            
            hole_obj = self.doc.addObject("Part::Feature", name)
            hole_obj.Shape = hole_shape
            
            return hole_obj
            
        except Exception as e:
            print(f"Error creating hex hole: {e}")
            traceback.print_exc()
            return None
    
    def safe_boolean_operation(self, shape1, shape2, operation="fuse"):
        """Perform boolean operations with error handling"""
        try:
            if not shape1.isValid() or not shape2.isValid():
                raise RuntimeError("Input shapes are invalid")
            
            if operation == "fuse":
                result = shape1.fuse(shape2)
            elif operation == "cut":
                result = shape1.cut(shape2)
            elif operation == "common":
                result = shape1.common(shape2)
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            if not result.isValid():
                raise RuntimeError(f"Boolean {operation} resulted in invalid shape")
            
            return result
            
        except Exception as e:
            print(f"Error in boolean {operation}: {e}")
            return None
    
    def design_wrench(self):
        """Main design method with comprehensive error handling"""
        if not self.load_modules():
            return False
            
        try:
            # Create document
            self.doc = self.FreeCAD.newDocument("RobustWrench")
            
            # Define parameters
            params = {
                'handle_length': 150,
                'handle_width': 15,
                'handle_thickness': 8,
                'head_length': 25,
                'head_width': 30,
                'hex_size': 8
            }
            
            # Create components
            print("Creating handle...")
            handle = self.create_safe_box(
                params['handle_length'], 
                params['handle_width'], 
                params['handle_thickness'], 
                "Handle"
            )
            
            if not handle:
                return False
            
            print("Creating head...")
            head = self.create_safe_box(
                params['head_length'], 
                params['head_width'], 
                params['handle_thickness'], 
                "Head"
            )
            
            if not head:
                return False
            
            # Position head
            offset_y = (params['head_width'] - params['handle_width']) / 2
            head.Placement.Base = self.FreeCAD.Vector(params['handle_length'], -offset_y, 0)
            
            print("Creating hex hole...")
            hex_center = [
                params['handle_length'] + params['head_length'] / 2,
                0,
                0
            ]
            
            hex_hole = self.create_safe_hex_hole(
                hex_center, 
                params['hex_size'], 
                params['handle_thickness'],
                "HexHole"
            )
            
            if not hex_hole:
                return False
            
            print("Assembling wrench...")
            # Fuse handle and head
            fused_shape = self.safe_boolean_operation(handle.Shape, head.Shape, "fuse")
            if not fused_shape:
                return False
            
            # Cut hex hole
            final_shape = self.safe_boolean_operation(fused_shape, hex_hole.Shape, "cut")
            if not final_shape:
                return False
            
            # Create final object
            wrench = self.doc.addObject("Part::Feature", "Wrench")
            wrench.Shape = final_shape
            
            # Set colors
            if hasattr(wrench, 'ViewObject'):
                wrench.ViewObject.ShapeColor = (0.5, 0.5, 0.8)
            
            # Hide intermediate objects
            for obj in [handle, head, hex_hole]:
                if hasattr(obj, 'ViewObject'):
                    obj.ViewObject.Visibility = False
            
            # Recompute
            self.doc.recompute()
            
            print("✓ Wrench design completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error in wrench design: {e}")
            traceback.print_exc()
            return False

# Usage
if __name__ == "__main__":
    designer = RobustWrenchDesigner()
    success = designer.design_wrench()
    print(f"Design {'succeeded' if success else 'failed'}")
```

## Best Practices Summary

1. **Always check object validity** before operations
2. **Use try-except blocks** around all FreeCAD operations
3. **Validate input parameters** before creating geometry
4. **Provide fallback methods** for missing modules
5. **Clean up objects** and documents properly
6. **Use descriptive error messages** for debugging
7. **Test with minimal examples** before complex designs
8. **Check FreeCAD version compatibility** if using newer features

## Quick Fixes Checklist

- [ ] All required modules imported correctly
- [ ] Object creation checked for success
- [ ] Shape validity verified before operations
- [ ] Proper error handling in place
- [ ] Alternative methods for missing features
- [ ] Document cleanup implemented
- [ ] Template paths verified for TechDraw
- [ ] PDF export with fallback options

This guide should help resolve most common FreeCAD wrench design errors!