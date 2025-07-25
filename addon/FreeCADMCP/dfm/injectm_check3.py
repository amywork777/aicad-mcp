import FreeCAD as App
import FreeCADGui as Gui
import Part
import Draft
import math
import random

from .base_checker import DFMChecker, get_face_name


class IMDFMChecker(DFMChecker):
    def __init__(self, 
            doc=None, 
            min_wall_thickness=0.5, 
            max_wall_thickness=4.0, 
            min_draft_angle=0.5, 
            min_internal_corner_radius=0.25, 
            max_aspect_ratio=5.0
        ):
        """
        Initialize the Injection Molding DFM checker with configuration specific to the injection molding process.
        
        Args:
            doc: FreeCAD document to check (defaults to active document)
            min_wall_thickness: Minimum wall thickness in mm
            max_wall_thickness: Maximum wall thickness in mm
            min_draft_angle: Minimum draft angle in degrees
            min_fillet_radius: Minimum fillet radius in mm
            max_aspect_ratio: Maximum aspect ratio for features
        """
        super(IMDFMChecker, self).__init__(doc, min_wall_thickness, max_wall_thickness)
        
        # DFM rules for injection molding
        self.min_draft_angle = min_draft_angle
        self.min_internal_corner_radius = min_internal_corner_radius
        self.max_aspect_ratio = max_aspect_ratio
        
        # Dictionary to store issues
        self.issues["draft_angles"] = []
        self.issues["sharp_corners"] = []
        self.issues["undercuts"] = []
        self.issues["high_aspect_ratio"] = []
        
        # Color schemes for highlighting issues
        self.color_schemes["draft_angles"] = (1.0, 0.5, 0.0)  # Orange
        self.color_schemes["sharp_corners"] = (1.0, 0.0, 0.0)  # Red
        self.color_schemes["undercuts"] = (0.0, 1.0, 0.0)  # Green
        self.color_schemes["high_aspect_ratio"] = (1.0, 0.0, 1.0)  # Purple
        
        # Default mold opening direction
        self.core_direction = App.Vector(0, 0, 1)
        self.parting_line = None
    
    def set_core_direction(self, direction=App.Vector(0, 0, 1)):
        """Set the mold opening/core direction."""
        self.core_direction = direction.normalize()
    
    def create_parting_line(self, shape):
        """
        Attempt to detect a reasonable parting line for the mold.
        This is a simplified approach - real parting line detection is more complex.
        """
        # TODO: Should be related to self.core_direction, but for now ony vertical direction is supported!
        # Find the bounding box
        bbox = shape.BoundBox
        mid_z = (bbox.ZMin + bbox.ZMax) / 2        
        # Create a parting plane at the middle height
        self.parting_line = Part.makePlane(
            bbox.XLength + 10,
            bbox.YLength + 10,
            App.Vector(bbox.XMin - 5, bbox.YMin - 5, mid_z)
        )        
        # Create a visual representation of the parting line
        parting_line_obj = self.doc.addObject("Part::Feature", "Parting_Line")
        parting_line_obj.Shape = self.parting_line
        parting_line_obj.ViewObject.Transparency = 80
        parting_line_obj.ViewObject.ShapeColor = (0.5, 0.5, 1.0)
        self.additional_objects.append(parting_line_obj.Name)
        
        return self.parting_line
    
    def run_all_checks(self):
        """Main analysis method to check all DFM rules."""
        print("Running Injection Molding DFM checks...")
        for obj in self.doc.Objects:
            if hasattr(obj, "Shape") and hasattr(obj, "ViewObject") and obj.ViewObject.Visibility:
                print(f"Checking object: {obj.Label}")             
                # Run all checks on this object
                        
                # Detect potential parting line
                self.create_parting_line(obj.Shape)
        
                # Run all analysis checks
                try:
                    self.check_draft_angles(obj)
                except Exception as e:
                    print(f"Check draft angles error: {str(e)}")
                    self.success = False
                try:
                    self.check_wall_thickness(obj)
                except Exception as e:
                    print(f"Check wall thickness error: {str(e)}")
                    self.success = False
                try:
                    self.check_sharp_corners(obj)
                except Exception as e:
                    print(f"Check sharp corners error: {str(e)}")
                    self.success = False
                try:
                    self.check_undercuts(obj)
                except Exception as e:
                    print(f"Check undercuts error: {str(e)}")
                    self.success = False
                try:
                    self.check_aspect_ratio(obj)
                except Exception as e:
                    print(f"Check aspect ratio error: {str(e)}")
                    self.success = False
                
        print("Before report")
        # Create summary report
        report_text = self.create_report()
        print("After report")
        
        # Recompute document
        self.doc.recompute()
        print("DFM Analysis completed.")
        return self.issues, report_text
    
    def check_draft_angles(self, obj):
        """Check if the model has sufficient draft angles for mold release."""
        shape = obj.Shape
        for face in shape.Faces:
            if face.Surface.isPlanar():
                # Get the normal of the face
                normal = face.normalAt(0, 0)  # for planar surface point does not matter                
                # Calculate angle with core direction
                angle = abs(math.degrees(normal.getAngle(self.core_direction)))
                # draft angle - angle between plane and the vertical direction
                # draft angle 0 corresponds to the angle between the core_direction and the normal 90 deg
                if (angle > 90 - self.min_draft_angle) and (angle < 90 + self.min_draft_angle):
                    self.highlight_feature(face, obj, "LowDraftAngle", "draft_angles")                
                    self.issues["draft_angles"].append({
                        "object": obj.Label,
                        "face": get_face_name(face, obj),
                        "location": f"Face at {face.CenterOfMass}",
                        "draft_angle": angle - 90,
                        "required": self.min_draft_angle
                    })
            else:
                for edge in face.Edges:
                    if edge.Curve.TypeId == 'Part::GeomLine':
                        direction_vector = edge.Curve.Direction
                        angle = abs(math.degrees(direction_vector.getAngle(self.core_direction)))
                        if (angle < self.min_draft_angle) or (angle > 180 - self.min_draft_angle):
                            self.highlight_feature(face, obj, "LowDraftAngle", "draft_angles")                
                            self.issues["draft_angles"].append({
                                "object": obj.Label,
                                "face": get_face_name(face, obj),
                                "location": f"Face at {face.CenterOfMass}",
                                "edge_draft_angle": angle,
                                "required": self.min_draft_angle
                            })
                            break
    
    def check_sharp_corners(self, obj):
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
    
    def check_undercuts(self, obj):
        """
        Check for undercuts that would prevent mold release.
        Simplified approach - real undercut detection is more complex.
        """
        displacement = 0.001
        grid_steps = 5
        print("Checking undercuts...")
        shape = obj.Shape
        if not self.parting_line:
            self.detect_parting_line(shape)            
        try:
            core_dir = App.Vector(self.core_direction)
            for face in shape.Faces:
                undercut_found = False
                u_min, u_max, v_min, v_max  = face.ParameterRange[: 4]
                u_size = u_max - u_min
                v_size = v_max - v_min
                if u_size > v_size:
                    u_steps = grid_steps + 1
                    v_steps = max(1, int(grid_steps * float(v_size) / float(u_size))) + 1
                else:
                    v_steps = grid_steps + 1
                    u_steps = max(1, int(grid_steps * float(u_size) / float(v_size))) + 1
                u_step = float(u_size) / u_steps
                v_step = float(v_size) / v_steps
                for uidx in range(0, u_steps + 1):
                    cur_u = u_min + uidx * u_step
                    for vidx in range(0, v_steps + 1):
                        cur_v = v_min + vidx * v_step
                        normal = face.normalAt(cur_u, cur_v)
                        pt = face.Surface.value(cur_u, cur_v)
                        # project point onto section plane
                        try:
                            ppt = project_point_onto_part_feature(self.parting_line, pt)
                        except Exception as e:
                            print(f"Point projection problem: {str(e)}")
                            continue
                        up_side = pt.z >= self.parting_line.BoundBox.ZMin
                        cos = normal.dot(core_dir)
                        if cos == 0:
                            # perpendicular direction
                            continue
                        # displace the point a bit to the plane to be sure that the ray not intersect the current face
                        if up_side:
                            pt.z -= displacement
                        else:
                            pt.z += displacement
                        if (up_side and cos > 0) or (not up_side and cos < 0):
                            intersections_allowed = 1 # normal is colinear to the direction from ppt to pt, one intersection is possible
                        else:
                            intersections_allowed = 0 # normal has the opposite direction, no intersections are allowed  
                        # ray casting
                        ray = Part.Line(pt, ppt)
                        intersections = shape.section([ray]).Vertexes
                        zmin = min(pt.z, ppt.z)
                        zmax = max(pt.z, ppt.z)
                        intersections = [v for v in intersections if (v.Point.z >= zmin) and (v.Point.z <= zmax)]
                        if len(intersections) > intersections_allowed:
                            # more intersections than allowed - undercut
                            self.highlight_feature(face, obj, "Undercut", "undercuts")                
                            self.issues["undercuts"].append({
                                "object": obj.Label,
                                "face": get_face_name(face, obj),
                                "location": f"Face at {face.CenterOfMass}",
                                "metric": len(intersections),
                                "required": intersections_allowed
                            })
                            undercut_found = True
                            break
                    if undercut_found:
                        break
        except Exception as e:
            print(f"Error analyzing undercuts: {str(e)}\n")
    
    def check_aspect_ratio(self, obj):
        """Check for features with high aspect ratios that might be unstable"""
        # TODO: Clarify, what we should check here - holes, sticks or both
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
        if issue_type == "wall_thickness":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has wall thickness of {issue['thickness']:.2f}mm (conditions: {issue['required']}mm)"
        elif issue_type == "draft_angles":
            if "draft_angle" in issue:
                return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has too small draft angle with draft angle {issue['draft_angle']:.2f} and conditin (required: {issue['required']})"
            else:
                return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has too small draft angle with edge draft angle {issue['edge_draft_angle']:.2f} and conditin (required: {issue['required']})"
        elif issue_type == "sharp_corners":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has sharp corner with curvature {issue['curvature']:.2f} (required: {issue['required']})"
        elif issue_type == "undercuts":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has undercut with {issue['metric']} intersections and {issue['required']} required intersections"
        elif issue_type == "high_aspect_ratio":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has {issue['feature_type']} with aspect ratio of {issue['ratio']:.2f} (max: {issue['required']})"
        else:
            return str(issue)


def project_point_onto_part_feature(plane_obj, point):
    """
    Project a point onto a plane defined by a Part::Feature object.    
    Args:
        plane_obj: A Part::Feature object or Part.Face that represents a planar surface
        point: A FreeCAD.Vector or Part.Vertex to project onto the plane
        
    Returns:
        FreeCAD.Vector: The projected point on the plane
    """
    if isinstance(point, Part.Vertex):
        point_vector = point.Point
    elif isinstance(point, App.Base.Vector):
        point_vector = point
    else:
        raise TypeError("Point must be a FreeCAD.Vector or Part.Vertex")    
    if hasattr(plane_obj, 'Shape'):
        # It's a Part::Feature object
        shape = plane_obj.Shape
        if not shape.Faces:
            raise ValueError("The Part::Feature does not contain any faces")
        face = shape.Faces[0]
    elif isinstance(plane_obj, Part.Face):
        # It's already a Face object
        face = plane_obj
    else:
        raise TypeError("plane_obj must be a Part::Feature object or a Part.Face")
    plane_normal = face.normalAt(0, 0)  # Get normal at parameter (0,0), for plane point not important
    plane_point = face.CenterOfMass    # Use center of mass as a point on the plane    
    v = point_vector.sub(plane_point)    
    dist = v.dot(plane_normal)    
    projected_point = point_vector.sub(plane_normal.multiply(dist))    
    return projected_point


def run_im_dfm_checker(
        doc_name=None, 
        min_wall_thickness=0.5, 
        max_wall_thickness=4.0, 
        min_draft_angle=0.5, 
        min_internal_corner_radius=0.25, 
        max_aspect_ratio=5.0
    ):
    """Run the Injection Molding DFM analyzer on the active document with the specified parameters"""
    print("Injection Molding DFM check started.")
    if (not App.ActiveDocument) and (doc_name is None):
        print("No active document. Please open or create a document first.")
        return
        
    if doc_name is not None:
        doc = App.getDocument(doc_name)
    else:
        doc = None
        
    checker = IMDFMChecker(
        doc=doc,
        min_wall_thickness=min_wall_thickness,
        max_wall_thickness=max_wall_thickness,
        min_draft_angle=min_draft_angle,
        min_internal_corner_radius=min_internal_corner_radius,
        max_aspect_ratio=max_aspect_ratio
    )
    issues, report_text = checker.run_all_checks()
    
    # Change to problem highlight view
    if any(issues.values()) and App.GuiUp:
        Gui.ActiveDocument.activeView().viewAxonometric()
        Gui.SendMsgToActiveView("ViewFit")
    
    print("Injection Molding DFM check completed.")
    return checker.success, issues, report_text, checker


# Add a simple UI to run the checks
if App.GuiUp:
    from PySide import QtCore, QtGui
    
    class InjectionMoldingDFMCheckerDialog(QtGui.QDialog):
        def __init__(self):
            super(InjectionMoldingDFMCheckerDialog, self).__init__()
            self.setWindowTitle("Injection Molding DFM Analyzer")
            self.resize(350, 250)
            
            layout = QtGui.QVBoxLayout()
            
            # Parameter inputs
            form_layout = QtGui.QFormLayout()
            
            self.min_thickness_spin = QtGui.QDoubleSpinBox()
            self.min_thickness_spin.setRange(0.1, 100.0)
            self.min_thickness_spin.setValue(0.5)
            self.min_thickness_spin.setSuffix(" mm")
            
            self.max_thickness_spin = QtGui.QDoubleSpinBox()
            self.max_thickness_spin.setRange(1.0, 100.0)
            self.max_thickness_spin.setValue(4.0)
            self.max_thickness_spin.setSuffix(" mm")
            
            self.draft_angle_spin = QtGui.QDoubleSpinBox()
            self.draft_angle_spin.setRange(0.1, 180.0)
            self.draft_angle_spin.setValue(0.5)
            self.draft_angle_spin.setSuffix("°")
            
            self.fillet_radius_spin = QtGui.QDoubleSpinBox()
            self.fillet_radius_spin.setRange(0.1, 100.0)
            self.fillet_radius_spin.setValue(0.25)
            self.fillet_radius_spin.setSuffix(" mm")
            
            self.aspect_ratio_spin = QtGui.QDoubleSpinBox()
            self.aspect_ratio_spin.setRange(1.0, 100.0)
            self.aspect_ratio_spin.setValue(5.0)
            
            form_layout.addRow("Min. Wall Thickness:", self.min_thickness_spin)
            form_layout.addRow("Max. Wall Thickness:", self.max_thickness_spin)
            form_layout.addRow("Min. Draft Angle:", self.draft_angle_spin)
            form_layout.addRow("Min. Fillet Radius:", self.fillet_radius_spin)
            form_layout.addRow("Max. Aspect Ratio:", self.aspect_ratio_spin)
            
            # Run button
            self.run_button = QtGui.QPushButton("Run Injection Molding DFM Check")
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
                "wall_thickness": (0.0, 1.0, 1.0),  # Cyan
                "draft_angles": (1.0, 0.5, 0.0),  # Orange
                "sharp_corners": (1.0, 0.0, 0.0),  # Red
                "undercuts": (0.0, 1.0, 0.0),  # Green
                "high_aspect_ratio": (1.0, 0.0, 1.0),  # Purple
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
            self.current_checker = None
        
        def run_check(self):
            self.status_label.setText("Status: Running Injection Molding DFM checks...")
            
            # Run the checker
            try:
                # Restore colors from previous run if any
                if self.current_checker:
                    self.current_checker.restore_original_colors()
                    self.current_checker.remove_additional_objects()
                
                # Run the new check
                success, issues, report_text, checker = run_im_dfm_checker(
                    doc_name = None,
                    min_wall_thickness=self.min_thickness_spin.value(),
                    max_wall_thickness=self.max_thickness_spin.value(),
                    min_draft_angle=self.draft_angle_spin.value(),
                    min_internal_corner_radius=self.fillet_radius_spin.value(),
                    max_aspect_ratio=self.aspect_ratio_spin.value()
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

