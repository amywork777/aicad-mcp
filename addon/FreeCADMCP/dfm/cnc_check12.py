import FreeCAD as App
import FreeCADGui as Gui
import Part
import math
import random
import os
from typing import Dict, Any

from .base_checker import DFMChecker, get_face_name


class CNCDFMChecker (DFMChecker):
    def __init__(self, doc=None, min_radius=1.0, max_aspect_ratio=4.0, min_internal_corner_radius=0.5, min_wall_thickness=1.0):
        """
        Initialize the CNC machining DFM checker with configuration specific to the machining process.
        
        Args:
            doc: FreeCAD document to check (defaults to active document)
            min_radius: Minimum tool radius in mm
            max_aspect_ratio: Maximum allowed depth to width ratio for pockets/holes
            min_internal_corner_radius: Minimum internal corner radius in mm
            min_wall_thickness: Minimum wall thickness in mm
        """
        super(CNCDFMChecker, self).__init__(doc, min_wall_thickness)
        
        # DFM rules
        self.min_radius = min_radius
        self.max_aspect_ratio = max_aspect_ratio
        self.min_internal_corner_radius = min_internal_corner_radius
        # min_wall_thickness is a part of base class
        
        # Dictionary to store issues
        self.issues["sharp_corners"] = []
        self.issues["small_radius"] = []
        self.issues["high_aspect_ratio"] = []
        
        # Color schemes for highlighting issues
        self.color_schemes["sharp_corners"] = (1.0, 0.0, 0.0)  # Red
        self.color_schemes["small_radius"] = (1.0, 0.5, 0.0)  # Orange
        self.color_schemes["high_aspect_ratio"] = (1.0, 0.0, 1.0)  # Purple
            
    def run_all_checks(self):
        """Run all CNC DFM checks on the document and highlight issues"""
        self.success = True
        print("Running CNC machining DFM checks...")
        
        # Check each visible object in the document
        for obj in self.doc.Objects:
            if hasattr(obj, "Shape") and hasattr(obj, "ViewObject") and obj.ViewObject.Visibility:
                print(f"Checking object: {obj.Label}")             
                # Run all checks on this object
                try:
                    self.check_sharp_internal_corners(obj)
                except Exception as e:
                    print(f"Check sharp internal corners error: {str(e)}")
                    self.success = False
                try:
                    self.check_small_radius_features(obj)
                except Exception as e:
                    print(f"Check small radius error: {str(e)}")
                    self.success = False
                try:
                    self.check_high_aspect_ratio(obj)
                except Exception as e:
                    print(f"Check high aspect ratio error: {str(e)}")
                    self.success = False
                try:
                    self.check_wall_thickness(obj)
                except Exception as e:
                    print(f"Check wall thickness error: {str(e)}")
                    self.success = False
        
        # Create summary report
        report_text = self.create_report()
        
        # Recompute document
        self.doc.recompute()
        print("DFM Analysis completed.")
        return self.issues, report_text
    
    def check_sharp_internal_corners(self, obj):
        """Check for sharp internal corners in the object"""
        print("Checking sharp corners...")
        shape = obj.Shape        
        # Look at all the edges that form internal corners
        curvature_limit = 1.0 / self.min_internal_corner_radius
        for face in shape.Faces:
            for edge in face.Edges:
                center = edge.CenterOfMass
                par = edge.Curve.parameter(center)
                # print("Edge curvature = ", edge.curvatureAt(par), " limit = ", curvature_limit)
                if edge.curvatureAt(0) > curvature_limit:  # Curvature is 1/radius
                    # This is a sharp internal corner
                    self.highlight_feature(face, obj, "SharpCorner", "sharp_corners")                
                    self.issues["sharp_corners"].append({
                        "object": obj.Label,
                        "face": get_face_name(face, obj),
                        "location": f"Face at {face.CenterOfMass}",
                        "curvature": edge.curvatureAt(par),
                        "required": f"< {curvature_limit}"
                    })
                    break
        # grid_steps = 5
        # for face in shape.Faces:
            # face_checked = False
            # if not hasattr(face, "Surface"):
                # continue
            # u_min, u_max, v_min, v_max = face.Surface.bounds()
            # u_size = u_max - u_min
            # v_size = v_max - v_min
            # if u_size > v_size:
                # u_steps = grid_steps + 1
                # v_steps = max(1, int(grid_steps * float(v_size) / float(u_size))) + 1
            # else:
                # v_steps = grid_steps + 1
                # u_steps = max(1, int(grid_steps * float(u_size) / float(v_size))) + 1
            # u_step = float(u_size) / u_steps
            # v_step = float(v_size) / v_steps
            # for uidx in range(0, u_steps + 1):
                # cur_u = u_min + uidx * u_step
                # for vidx in range(0, v_steps + 1):
                    # cur_v = v_min + vidx * v_step
                    # max_curvature = face.Surface.curvature(cur_u, cur_v, "Max")
                    # # curvature_dir = face.Surface.curvatureDirections(cur_u, cur_v)
                    # # max_curvature = max(abs(curvature_dir[0][0]), abs(curvature_dir[1][0]))
                    # # print("Curvature dir = ", curvature_dir)
                    # print("Curvature = ", max_curvature, " Limit = ", curvature_limit)
                    # if max_curvature > curvature_limit:
                        # # This is a sharp internal corner
                        # self.highlight_feature(face, obj, "SharpCorner", "sharp_corners")                
                        # self.issues["sharp_corners"].append({
                            # "object": obj.Label,
                            # "location": f"Face at {face.CenterOfMass}",
                            # "curvature": max_curvature,
                            # "required": f"< {curvature_limit}"
                        # })
                        # face_checked = True
                        # break
                # if face_checked:
                    # break
    
    def check_small_radius_features(self, obj):
        """Check for features with radius smaller than minimum tool radius"""
        print("Checking small radius features...")
        shape = obj.Shape        
        for face in shape.Faces:
            if hasattr(face, "Surface") and hasattr(face.Surface, "Radius"):
                # print("Face radius = ", face.Surface.Radius)
                if face.Surface.Radius < self.min_radius:
                    feature_detected = True
                    if hasattr(face.Surface, "Center"):
                        center = face.Surface.Center
                    elif hasattr(face.Surface, "Location"):
                        center = face.Surface.Location
                    elif hasattr(face.Surface, "Position"):
                        center = face.Surface.Position
                    else:
                        center = None
                    if center is not None:
                        center_mass_uv = face.Surface.parameter(face.CenterOfMass)
                        normal = face.normalAt(center_mass_uv[0], center_mass_uv[1])
                        center_mass = face.Surface.value(center_mass_uv[0], center_mass_uv[1])
                        vec = center_mass.sub(center)
                        cos_val = vec.dot(normal)
                        if cos_val > 0:
                            feature_detected = False
                    if feature_detected:
                        self.highlight_feature(face, obj, "SmallRadius", "small_radius")                    
                        self.issues["small_radius"].append({
                            "object": obj.Label,
                            "face": get_face_name(face, obj),
                            "location": f"Face at {face.CenterOfMass}",
                            "radius": face.Surface.Radius,
                            "required": self.min_radius
                        })
    
    def check_high_aspect_ratio(self, obj):
        """
        Check for features with high depth to width ratio
        Uses a more robust approach for detecting holes, pockets, and slots
        """
        print("Checking high aspect ratio...")
        shape = obj.Shape       
        for face in shape.Faces:
            if hasattr(face, "Surface") and isinstance(face.Surface, Part.Cylinder):
                cylinder = face.Surface
                axis = App.Vector(cylinder.Axis)
                axis.normalize()            
                # Use the face's bounding box to find a point on the axis
                # We'll use the center of mass of the face as a reference point
                ref_point = face.CenterOfMass
                # Collect all vertices of the face
                vertices = []
                for edge in face.Edges:
                    vertices.extend([v.Point for v in edge.Vertexes])
                if not vertices:
                    continue
                # TODO - check the angle between the direction to the center and normal to ensure that this is a hole, not a stick
                # Project all vertices onto the axis
                # We use parametric line equation: projection = ref_point + t * axis
                # where t = (vertex - ref_point) • axis
                projections = []
                for vertex in vertices:
                    vec = vertex - ref_point
                    t = vec.dot(axis)
                    projections.append(t)            
                # The height is the difference between max and min projections
                # print("Cylinder with ", len(projections))
                if projections:
                    height = max(projections) - min(projections)                
                    radius = face.Surface.Radius
                    # print("Height = ", height, " radius = ", radius, " ratio = ", height / (2 * radius))
                    if height / (2 * radius) > self.max_aspect_ratio:
                        self.highlight_feature(face, obj, "HighAspectRatio", "high_aspect_ratio")                
                        self.issues["high_aspect_ratio"].append({
                            "object": obj.Label,
                            "face": get_face_name(face, obj),
                            "location": f"Face at {face.CenterOfMass}",
                            "feature_type": "cylindrical hole",
                            "radius": radius,
                            "depth": height,
                            "ratio": height / (2*radius),
                            "required": self.max_aspect_ratio
                        })
            
    def format_issue(self, issue_type, issue):
        """Format a specific issue for the report"""
        if issue_type == "sharp_corners":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has sharp corner with curvature {issue['curvature']:.2f} (required: {issue['required']})"
        elif issue_type == "small_radius":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has radius of {issue['radius']:.2f}mm (min: {issue['required']}mm)"
        elif issue_type == "high_aspect_ratio":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has {issue['feature_type']} with aspect ratio of {issue['ratio']:.2f} (max: {issue['required']})"
        elif issue_type == "wall_thickness":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has wall thickness of {issue['thickness']:.2f}mm (conditions: {issue['required']}mm)"
        else:
            return str(issue)


def run_cnc_dfm_checker(doc_name = None, min_radius=1.0, max_aspect_ratio=4.0, min_internal_corner_radius=0.5, min_wall_thickness=1.0):
    """Run the CNC DFM checker on the active document with the specified parameters"""
    print("CNC DFM check started.")
    if (not App.ActiveDocument) and (doc_name is None):
        print("No active document. Please open or create a document first.")
        return
        
    if doc_name is not None:
        doc = App.getDocument(doc_name)
    else:
        doc = None
        
    checker = CNCDFMChecker(
        doc=doc,
        min_radius=min_radius,
        max_aspect_ratio=max_aspect_ratio,
        min_internal_corner_radius=min_internal_corner_radius,
        min_wall_thickness=min_wall_thickness
    )
    issues, report_text = checker.run_all_checks()
    
    # Change to problem highlight view
    if any(issues.values()) and App.GuiUp:
        Gui.ActiveDocument.activeView().viewAxonometric()
        Gui.SendMsgToActiveView("ViewFit")
    
    print("CNC DFM check completed.")
    return checker.success, issues, report_text, checker
    

# Add a simple UI to run the checks
if App.GuiUp:
    from PySide import QtCore, QtGui
    
    class CNCDFMCheckerDialog(QtGui.QDialog):
        def __init__(self):
            super(CNCDFMCheckerDialog, self).__init__()
            self.setWindowTitle("CNC Machining DFM Checker")
            self.resize(350, 300)
            
            layout = QtGui.QVBoxLayout()
            
            # Parameter inputs
            form_layout = QtGui.QFormLayout()
            
            self.radius_spin = QtGui.QDoubleSpinBox()
            self.radius_spin.setRange(0.1, 100.0)
            self.radius_spin.setValue(1.0)
            self.radius_spin.setSuffix(" mm")
            
            self.corner_radius_spin = QtGui.QDoubleSpinBox()
            self.corner_radius_spin.setRange(0.1, 100.0)
            self.corner_radius_spin.setValue(0.5)
            self.corner_radius_spin.setSuffix(" mm")
            
            self.aspect_ratio_spin = QtGui.QDoubleSpinBox()
            self.aspect_ratio_spin.setRange(1.0, 100.0)
            self.aspect_ratio_spin.setValue(4.0)
            
            self.wall_thickness_spin = QtGui.QDoubleSpinBox()
            self.wall_thickness_spin.setRange(0.1, 100.0)
            self.wall_thickness_spin.setValue(1.0)
            self.wall_thickness_spin.setSuffix(" mm")
            
            form_layout.addRow("Min. Tool Radius:", self.radius_spin)
            form_layout.addRow("Min. Corner Radius:", self.corner_radius_spin)
            form_layout.addRow("Max. Depth/Width Ratio:", self.aspect_ratio_spin)
            form_layout.addRow("Min. Wall Thickness:", self.wall_thickness_spin)
            
            # Run button
            self.run_button = QtGui.QPushButton("Run CNC DFM Check")
            self.run_button.clicked.connect(self.run_check)
            
            # Restore colors button
            self.restore_button = QtGui.QPushButton("Restore Original Colors")
            self.restore_button.clicked.connect(self.restore_colors)
            self.restore_button.setEnabled(False)
            
            # Status label
            self.status_label = QtGui.QLabel("Status: Ready")
            
            # Add widgets to layout
            layout.addLayout(form_layout)
            layout.addWidget(self.run_button)
            layout.addWidget(self.restore_button)
            layout.addWidget(self.status_label)

            color_schemes = {
                "sharp_corners": (1.0, 0.0, 0.0),  # Red
                "small_radius": (1.0, 0.5, 0.0),  # Orange
                "high_aspect_ratio": (1.0, 0.0, 1.0),  # Purple
                "wall_thickness": (0.0, 1.0, 1.0)  # Cyan
            }
            self.color_labels = []
            for key in color_schemes:
                color_label = QtGui.QLabel("Detected: " + key.replace("_", " "))
                cl = color_schemes[key]
                values = "{r}, {g}, {b}, {a}".format(r = int(255 * cl[0]), g = int(255 * cl[1]), b = int(255 * cl[2]), a = 255)
                color_label.setStyleSheet("QLabel { color: rgba("+values+"); }")
                self.color_labels.append(color_label)
                layout.addWidget(color_label)
            
            self.setLayout(layout)
            
            # Store the current checker
            self.current_checker = None
        
        def run_check(self):
            self.status_label.setText("Status: Running CNC DFM checks...")
            
            # Run the checker
            try:
                # Restore colors from previous run if any
                if self.current_checker:
                    self.current_checker.restore_original_colors()
                    self.current_checker.remove_additional_objects()
                
                # Run the new check
                success, issues, report_text, checker = run_cnc_dfm_checker(
                    doc_name = None,
                    min_radius=self.radius_spin.value(),
                    max_aspect_ratio=self.aspect_ratio_spin.value(),
                    min_internal_corner_radius=self.corner_radius_spin.value(),
                    min_wall_thickness=self.wall_thickness_spin.value()
                )
                
                # Store the current checker for later restoration
                self.current_checker = checker
                
                # Enable the restore button
                self.restore_button.setEnabled(True)
                
                total_issues = sum(len(issue_list) for issue_list in issues.values())
                
                if total_issues == 0:
                    self.status_label.setText("Status: No issues found! Model is machinable.")
                else:
                    self.status_label.setText(f"Status: Found {total_issues} potential issues. See report for details.")
            except Exception as e:
                self.status_label.setText(f"Status: Error - {str(e)}")
        
        def restore_colors(self):
            """Restore original colors of highlighted objects"""
            if self.current_checker:
                self.current_checker.restore_original_colors()
                self.current_checker.remove_additional_objects()
                self.status_label.setText("Status: Original colors restored.")
                self.restore_button.setEnabled(False)
                self.current_checker = None

