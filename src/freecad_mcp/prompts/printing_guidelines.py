"""
Prompts for printing design guidelines in FreeCAD
"""

def get_cnc_machining_guidelines(dfm_information) -> str:
    """Design guidelines for optimizing 3D models for CNC machining"""
    return f"""
# Taiyaki AI MCP Prompt: CNC Machining Design Guidelines

## Overview

This prompt is tailored to help user design 3D models optimized for CNC Machining. The guideline cover key features like tolerance, holes diameter, wall thickness, etc. Practical examples in FreeCAD and relevant Python code snippets are provided to illustrate how to apply these rules during the design process.

## 1. General Process Parameters

Below there are a set of currently supported features (with its descriptions) for CNC Machining.
{dfm_information}

You should use this information for refining DFM rules using refine_cnc_machining_dfm() tool based on user question.

## 2. Best Practices for CNC Machining Design

### A. Design Considerations by Process

  - **Wall Thickness & Structural Integrity:**  
  Ensure walls meet or exceed the minimum wall thicknes. Thin walls may compromise structural integrity.

  - **Tolerances & Fit:**
  Account for the tolerance limits. Incorporate gradual transitions, avoid sharp corners, and design with proper allowances for post-processing.

  - **Feature-Specific Guidelines:**  
  When including engraved details, holes, or moving parts, ensure they adhere to the minimum sizes and clearances specific to the process. This is critical for moving components and fine details.

### B. Recommendations for Optimized CNC Machining Models

- **Material-Specific Adjustments:**  
  Adapt your design rules based on the material properties (e.g., metal vs. polymer) and the corresponding process requirements.

---

## 3. Practical FreeCAD Examples

### Example 1: Verifying Minimum Wall Thickness

#### Steps:
1. **Create Your Model:**  
   Begin by sketching your part ensuring walls are designed at or above the process minimum.
   
2. **Analyze Wall Thickness:**  
   Use FreeCAD's built-in measurement tools to verify that all wall sections meet the minimum required thickness for your chosen process (e.g., 0.4 mm for DMLS supported walls).

#### Python Code Snippet:
```python
import FreeCAD, Part

doc = FreeCAD.newDocument("3DPrint_WallThickness")
# Create a simple extruded part with variable wall thickness
sketch = Part.makeRectangle(50, 30)
solid = sketch.extrude(10)

# Pseudocode: Function to verify wall thickness
def verify_wall_thickness(solid, min_thickness):
    # This function would iterate through walls and check dimensions
    # In practice, use FreeCAD's measurement API or custom scripts
    valid = True
    # ... perform checks ...
    return valid

# Example: Set minimum thickness for a specific process (e.g., 0.4 mm)
min_thickness = 0.4
if verify_wall_thickness(solid, min_thickness):
    print("All walls meet the minimum thickness requirement.")
else:
    print("Warning: Some walls do not meet the minimum thickness requirement.")

Part.show(solid)
doc.recompute()
```

## 3. Summary & Next Steps

  - **Review Process Parameters:**  
  Consult the tables above to ensure your design parameters align with the capabilities of the intended 3D printing process.

  - **Apply Best Practices:**  
  Incorporate guidelines on wall thickness, tolerances, and feature details to enhance print reliability.

  - **Experiment in FreeCAD:**  
  Utilize the provided examples and code snippets to validate your design and make iterative improvements.

  - **Adapt and Optimize:**  
  Fine-tune your design by considering material-specific behavior and process constraints, ensuring a manufacturable, high-quality model.

  By following these detailed guidelines and leveraging FreeCAD for design validation, you can create optimized 3D models that are well-suited for CNC Machining
"""

def get_3d_printing_guidelines(dfm_information) -> str:
    """Design guidelines for optimizing 3D models for various printing technologies"""
    return f"""
# Taiyaki AI MCP Prompt: 3D Printing Design Guidelines

## Overview

This prompt is tailored to help users design 3D models optimized for various 3D printing processes. It provides detailed design rules for processes such as DMLS, SLA, SLS, MJF, Carbon DLS, PolyJet, FDM (Industrial & In-house), and Binder Jetting. The guidelines cover key features like resolution, layer thickness, minimum feature sizes, tolerances, wall thicknesses, and more. Practical examples in FreeCAD and relevant Python code snippets are provided to illustrate how to apply these rules during the design process.

## 1. Process-Specific Parameter

### A. General Process Parameters

Below there are a set of currently supported features (with its descriptions) and processes for 3D printing.
{dfm_information}

You should use this information for refining DFM rules using refine_3d_printing_dfm() tool.

## 2. Best Practices for 3D Printing Design

### A. Design Considerations by Process

- **Resolution & Detail:**  
  Match your design's layer thickness and minimum feature sizes to the capabilities of your chosen process. For example, SLA can achieve finer details (down to 0.006 in features) while FDM (In-house) might require larger features for reliability.

- **Wall Thickness & Structural Integrity:**  
  Ensure walls meet or exceed the minimum wall thickness for your process. Thin walls may compromise structural integrity, especially for Binder Jetting or FDM.

- **Tolerances & Fit:**  
  Account for the tolerance limits of each process. Incorporate gradual transitions, avoid sharp corners, and design with proper allowances for post-processing.

- **Overhangs & Supports:**  
  Design overhangs keeping in mind that features beyond a certain threshold (e.g., >0.020 in) may need support structures. For processes like FDM, ensure overhangs remain within the supported angle (e.g., 45°).

- **Feature-Specific Guidelines:**  
  When including engraved details, holes, or moving parts, ensure they adhere to the minimum sizes and clearances specific to the process. This is critical for moving components and fine details.

### B. Recommendations for Optimized 3D Printing Models

- **Consistency in Geometry:**  
  Use uniform wall thickness and avoid sudden changes in cross-section to prevent defects during printing.
  
- **Support Structure Strategy:**  
  Evaluate the need for supports early in the design, especially for overhangs and horizontal bridges. Consider incorporating escape holes in designs with enclosed cavities.
  
- **Material-Specific Adjustments:**  
  Adapt your design rules based on the material properties (e.g., metal vs. polymer) and the corresponding process requirements.

---

## 3. Practical FreeCAD Examples

### Example 1: Verifying Minimum Wall Thickness

#### Steps:
1. **Create Your Model:**  
   Begin by sketching your part ensuring walls are designed at or above the process minimum.
   
2. **Analyze Wall Thickness:**  
   Use FreeCAD's built-in measurement tools to verify that all wall sections meet the minimum required thickness for your chosen process (e.g., 0.4 mm for DMLS supported walls).

#### Python Code Snippet:
```python
import FreeCAD, Part

doc = FreeCAD.newDocument("3DPrint_WallThickness")
# Create a simple extruded part with variable wall thickness
sketch = Part.makeRectangle(50, 30)
solid = sketch.extrude(10)

# Pseudocode: Function to verify wall thickness
def verify_wall_thickness(solid, min_thickness):
    # This function would iterate through walls and check dimensions
    # In practice, use FreeCAD's measurement API or custom scripts
    valid = True
    # ... perform checks ...
    return valid

# Example: Set minimum thickness for a specific process (e.g., 0.4 mm)
min_thickness = 0.4
if verify_wall_thickness(solid, min_thickness):
    print("All walls meet the minimum thickness requirement.")
else:
    print("Warning: Some walls do not meet the minimum thickness requirement.")

Part.show(solid)
doc.recompute()
```

---

### Example 2: Checking Overhang Angles

#### Steps:
1. **Design with Overhangs in Mind:**  
   Create features that minimize overhang angles or include support structures as needed.
2. **Evaluate Overhang Angles:**  
   Use a custom Python function to identify any overhangs exceeding the recommended threshold (e.g., >45° for FDM).

#### Python Code Snippet:
```python
def check_overhangs(shape, max_angle=45):
    # Pseudocode: Analyze each face's orientation relative to the build platform
    overhang_faces = []
    for face in shape.Faces:
        # Compute the angle of the face (this is a placeholder for actual computation)
        face_angle = 0  # Replace with calculation logic
        if face_angle > max_angle:
            overhang_faces.append(face)
    return overhang_faces

# Example usage in FreeCAD
overhang_faces = check_overhangs(solid)
print("Overhang faces detected:", len(overhang_faces))
```

---

## 4. Summary & Next Steps

- **Review Process Parameters:**  
  Consult the tables above to ensure your design parameters align with the capabilities of the intended 3D printing process.
  
- **Apply Best Practices:**  
  Incorporate guidelines on wall thickness, overhangs, tolerances, and feature details to enhance print reliability.
  
- **Experiment in FreeCAD:**  
  Utilize the provided examples and code snippets to validate your design and make iterative improvements.
  
- **Adapt and Optimize:**  
  Fine-tune your design by considering material-specific behavior and process constraints, ensuring a manufacturable, high-quality 3D printed model.

By following these detailed guidelines and leveraging FreeCAD for design validation, you can create optimized 3D models that are well-suited to your chosen printing process.
"""


