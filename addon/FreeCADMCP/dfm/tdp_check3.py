import FreeCAD as App
import FreeCADGui as Gui
import Part
import Mesh
import MeshPart
import math
import Draft

from .base_checker import DFMChecker, get_face_name


class TDPDFMChecker(DFMChecker):
    def __init__(self, 
        doc=None, 
        process_type="FDM", 
        min_wall_thickness=1.0, 
        min_feature_size=0.8,  
        max_overhang_angle=45.0, 
        min_hole_radius=2.0, 
        min_text_size=2.0,
        min_vertical_wire_thickness = 1.0,
        min_clearance = 0.5,
        max_aspect_ratio = 20):
        """
        Initialize the DFM checker with configuration specific to the printing process.
        
        Args:
            doc: FreeCAD document to check (defaults to active document)
            process_type: Type of 3D printing process ("FDM", "SLA", "SLS", etc.)
        """
        super(TDPDFMChecker, self).__init__(doc, min_wall_thickness)
        self.process_type = process_type
        
        # Define DFM rules based on process type
        # Values in mm
        if process_type == "FDM":
            self.min_wall_thickness = 0.8
            self.min_feature_size = 0.6
            self.max_overhang_angle = 45.0  # degrees from vertical
            self.min_hole_radius = 1.0
            self.min_text_size = 2.0
            self.min_vertical_wire_thickness = 0.8
            self.min_clearance = 0.5
            self.max_aspect_ratio = 20  # For tall, thin features
        elif process_type == "SLA":
            self.min_wall_thickness = 0.5
            self.min_feature_size = 0.3
            self.max_overhang_angle = 30.0
            self.min_hole_radius = 0.5
            self.min_text_size = 1.0
            self.min_vertical_wire_thickness = 0.5
            self.min_clearance = 0.3
            self.max_aspect_ratio = 30
        elif process_type == "SLS":
            self.min_wall_thickness = 0.7
            self.min_feature_size = 0.5
            self.max_overhang_angle = 0.0  # No limit, powder supports everything
            self.min_hole_radius = 0.75
            self.min_text_size = 1.5
            self.min_vertical_wire_thickness = 0.7
            self.min_clearance = 0.5
            self.max_aspect_ratio = 40
        else:
            # Default to conservative FDM values
            self.min_wall_thickness = min_wall_thickness
            self.min_feature_size = min_feature_size
            self.max_overhang_angle = max_overhang_angle
            self.min_hole_radius = min_hole_radius
            self.min_text_size = min_text_size
            self.min_vertical_wire_thickness = min_vertical_wire_thickness
            self.min_clearance = min_clearance
            self.max_aspect_ratio = max_aspect_ratio
            
        self.mesh_deviation = 0.1  # Mesh accuracy for analysis
        
        # Dictionary to store issues
        self.issues["small_features"] = []
        self.issues["overhangs"] = []
        self.issues["small_radius"] = []
        self.issues["small_text"] = []
        self.issues["high_aspect_ratio"] = []
        self.issues["insufficient_clearance"] = []
        self.success = True
        
        # Color schemes for highlighting issues
        self.color_schemes["small_features"] = (0.0, 1.0, 0.0)  # Green
        self.color_schemes["overhangs"] = (1.0, 1.0, 0.0)  # Yellow
        self.color_schemes["small_radius"] = (1.0, 0.5, 0.0)  # Orange
        self.color_schemes["small_text"] = (1.0, 0.0, 0.0)  # Red
        self.color_schemes["high_aspect_ratio"] = (1.0, 0.0, 1.0)  # Purple
        self.color_schemes["insufficient_clearance"] = (0.0, 0.0, 1.0)  # Blue
        
        self.original_colors = {}
    
    def run_all_checks(self):
        """Run all DFM checks on the document and highlight issues"""
        self.success = True
        print(f"Running 3D Printing DFM checks for {self.process_type} process...")
        
        nobjects = len([o for o in self.doc.Objects if hasattr(o, "Shape")])
        # Check each visible object in the document
        for obj in self.doc.Objects:
            if hasattr(obj, "Shape") and hasattr(obj, "ViewObject") and obj.ViewObject.Visibility:
                print(f"Checking object: {obj.Label}")               
                # Run all checks on this object
                try:
                    self.check_wall_thickness(obj)
                except Exception as e:
                    print(f"Check wall thickness error: {str(e)}")
                    success = False
                try:
                    self.check_small_features(obj)
                except Exception as e:
                    print(f"Check small features error: {str(e)}")
                    success = False
                try:
                    self.check_overhangs(obj)
                except Exception as e:
                    print(f"Check overhangs error: {str(e)}")
                    success = False
                try:
                    self.check_small_radius_features(obj)
                except Exception as e:
                    print(f"Check small holes error: {str(e)}")
                    success = False
                try:
                    self.check_aspect_ratio(obj)
                except Exception as e:
                    print(f"Check high aspect ratio error: {str(e)}")
                    success = False
                
                # If we have multiple objects, check clearances between them
                if nobjects > 1:
                    try:
                        self.check_clearances(obj)
                    except Exception as e:
                        print(f"Check clearances error: {str(e)}")
                        success = False
        
        # Create summary report
        report_text = self.create_report()
        
        # Recompute document
        self.doc.recompute()
        print("DFM Analysis completed.")
        return self.issues, report_text
    
    def check_small_features(self, obj):
        """Check for features smaller than minimum printable size"""
        print("Checking small features...")
        shape = obj.Shape       
        # Look for small edges and vertices
        for face in shape.Faces:
            bbox = face.BoundBox
            lengths = [bbox.XLength, bbox.YLength, bbox.ZLength]
            lengths.sort()
            # at least two dimensions less than the threshold
            if lengths[1] < self.min_feature_size:
                self.highlight_feature(face, obj, "SmallFeature", "small_features")                
                self.issues["small_features"].append({
                    "object": obj.Label,
                    "face": get_face_name(face, obj),
                    "location": f"Face at {face.CenterOfMass}",
                    "max_size": lengths[1],
                    "required": self.min_feature_size,
                })
            # TODO: Think how it may be done better to analyze oriented bounding box
            # else:
                # for edge in face.Edges:
                    # if (edge.Length < self.min_feature_size):
                        # self.highlight_feature(face, obj, "SmallFeature", "small_features")                
                        # self.issues["small_features"].append({
                            # "object": obj.Label,
                            # "face": get_face_name(face, obj),
                            # "location": f"Face at {face.CenterOfMass}",
                            # "minimal_edge_size": edge.Length,
                            # "required": self.min_feature_size,
                        # })
                        # break
    
    def check_overhangs(self, obj):
        """Check for overhangs steeper than maximum printable angle"""
        if self.max_overhang_angle == 0.0:  # Skip for processes like SLS that don't have overhang limits
            return
        print("Checking overhangs...")    
        shape = obj.Shape     
        # Check face normals relative to build direction (Z-axis)
        build_direction = App.Vector(0, 0, 1)      
        for face_idx, face in enumerate(shape.Faces):
            # Stage 1 - Get the face normal at center of mass
            # u_mid = face.ParameterRange[0] + (face.ParameterRange[1] - face.ParameterRange[0])/2
            # v_mid = face.ParameterRange[2] + (face.ParameterRange[3] - face.ParameterRange[2])/2
            # try:
                # normal = face.normalAt(u_mid, v_mid)
                # # Calculate angle between normal and build direction
                # angle_rad = abs(normal.getAngle(build_direction))
                # angle_deg = math.degrees(angle_rad)
                # # Check if the face is pointing downward and exceeds overhang angle
                # # if angle_deg > 90 and (180 - angle_deg) > self.max_overhang_angle:
                # if angle_deg > 180 - self.max_overhang_angle:
                    # self.highlight_feature(face, obj, "Overhang", "overhangs")                
                    # self.issues["overhangs"].append({
                        # "object": obj.Label,
                        # "face": get_face_name(face, obj),
                        # "location": f"Face at {face.CenterOfMass}",
                        # "angle": angle_deg,
                        # "required": f"> 90, < 180 - {self.max_overhang_angle}",
                    # })
            # # TODO: Check overhang at edge vertices, maybe also at grid pointsß
            # except Exception as e:
                # print(f"Error checking face {face_idx} for overhangs: {e}")
            grid_steps = 5
            try:
                # u_min, u_max, v_min, v_max = face.Surface.bounds()
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
                        # Calculate angle between normal and build direction
                        angle_rad = abs(normal.getAngle(build_direction))
                        angle_deg = math.degrees(angle_rad)
                        # Check if the face is pointing downward and exceeds overhang angle
                        # if angle_deg > 90 and (180 - angle_deg) > self.max_overhang_angle:
                        if angle_deg > 180 - self.max_overhang_angle:
                            self.highlight_feature(face, obj, "Overhang", "overhangs")                
                            self.issues["overhangs"].append({
                                "object": obj.Label,
                                "face": get_face_name(face, obj),
                                "location": f"Face at {face.CenterOfMass}",
                                "angle": angle_deg,
                                # "required": f"> 90, < 180 - {self.max_overhang_angle}",
                                "required": f"< 180 - {self.max_overhang_angle}",
                            })
            except Exception as e:
                print(f"Error checking face {face_idx} for overhangs: {str(e)}")

    
    def check_small_radius_features(self, obj):
        """Check for features with radius smaller than minimum tool radius"""
        print("Checking small radius features...")
        shape = obj.Shape        
        for face in shape.Faces:
            if hasattr(face, "Surface") and hasattr(face.Surface, "Radius"):
                # print("Face radius = ", face.Surface.Radius)
                if face.Surface.Radius < self.min_hole_radius:
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
                            "required": self.min_hole_radius
                        })
    
        # try:
            # # 1. First detect circular and elliptical holes via edges
            # circular_holes = []
            
            # for edge in shape.Edges:
                # # Check for circular edges
                # if edge.Closed and isinstance(edge.Curve, Part.Circle):
                    # diameter = edge.Curve.Radius * 2
                    
                    # if diameter < self.min_hole_radius * 2:
                        # circular_holes.append({
                            # "center": edge.Curve.Center,
                            # "diameter": diameter,
                            # "shape": edge.copy(),
                            # "type": "circular"
                        # })
                
                # # Check for elliptical edges
                # elif edge.Closed and isinstance(edge.Curve, Part.Ellipse):
                    # # For ellipses, use the minor axis as the critical dimension
                    # major_radius = edge.Curve.MajorRadius
                    # minor_radius = edge.Curve.MinorRadius
                    # min_diameter = min(major_radius, minor_radius) * 2
                    
                    # if min_diameter < self.min_hole_radius * 2:
                        # circular_holes.append({
                            # "center": edge.Curve.Center,
                            # "diameter": min_diameter,
                            # "shape": edge.copy(),
                            # "type": "elliptical"
                        # })
            
            # # 3. Topological hole detection
            # # This approach finds holes by analyzing the model's topology
            # topological_holes = []            
            # # Create a shell from all faces
            # try:
                # shell = Part.Shell(shape.Faces)                
                # # For each vertex, check if it's part of a small hole by analyzing connected edges
                # for vertex in shape.Vertexes:
                    # # Get all edges connected to this vertex
                    # connected_edges = [e for e in shape.Edges if vertex.Point.distanceToPoint(e.Vertex1.Point) < 1e-5 or 
                                        # vertex.Point.distanceToPoint(e.Vertex2.Point) < 1e-5]                    
                    # if len(connected_edges) >= 3:  # Junction point, potential hole corner
                        # # Analyze the surrounding geometry to detect hole-like structures                       
                        # # Get vertices connected to this one through edges
                        # connected_vertices = []                       
                        # for edge in connected_edges:
                            # if edge.Vertex1.Point.distanceToPoint(vertex.Point) < 1e-5:
                                # connected_vertices.append(edge.Vertex2.Point)
                            # else:
                                # connected_vertices.append(edge.Vertex1.Point)
                        
                        # # Calculate distances between these vertices
                        # min_dist = float('inf')                        
                        # for i in range(len(connected_vertices)):
                            # for j in range(i+1, len(connected_vertices)):
                                # dist = connected_vertices[i].distanceToPoint(connected_vertices[j])
                                # if dist < min_dist:
                                    # min_dist = dist                       
                        # # If the minimum distance is less than our threshold, this might be part of a small hole
                        # if min_dist < self.min_hole_radius * 2 and min_dist > 0.01:  # Avoid numerical issues
                            # # Check if this vertex is already part of a detected hole
                            # already_detected = False                            
                            # # Check if within tolerance of existing hole
                            # for hole in topological_holes + circular_holes + rectangular_holes:
                                # if vertex.Point.distanceToPoint(hole["center"]) < self.min_hole_radius * 2:
                                    # already_detected = True
                                    # break                            
                            # if not already_detected:
                                # # Create a marker for this potential hole
                                # topological_holes.append({
                                    # "center": vertex.Point,
                                    # "diameter": min_dist,
                                    # "shape": vertex.copy(),
                                    # "type": "topological"
                                # })
            # except Exception as e:
                # # Shell creation can fail for non-manifold geometry
                # print(f"Topological analysis failed: {e}")
                
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
    
    def check_clearances(self, obj):
        """Check for insufficient clearances between moving or separate parts"""
        shape = obj.Shape        
        # Compare with all other objects
        for other in self.doc.Objects:
            if other == obj or not hasattr(other, "Shape"):
                continue
            other_shape = other.Shape
            try:
                # Calculate distance between shapes
                dist_info = shape.distToShape(other_shape)
                distance = dist_info[0]                
                if 0 < distance < self.min_clearance:
                    # Create lines showing insufficient clearances
                    for point_pair in dist_info[1]:
                        p1 = point_pair[0]
                        p2 = point_pair[1]
                        name = f"InsufficientClearance_{len(self.issues['insufficient_clearance'])}"
                        line = self.doc.addObject("Part::Line", name)
                        line.X1 = p1.x
                        line.Y1 = p1.y
                        line.Z1 = p1.z
                        line.X2 = p2.x
                        line.Y2 = p2.y
                        line.Z2 = p2.z
                        line.ViewObject.LineColor = self.color_schemes["insufficient_clearance"]
                        line.ViewObject.LineWidth = 3
                        self.additional_objects.append(name)                        
                        self.issues["insufficient_clearance"].append({
                            "object1": obj.Label,
                            "object2": other.Label,
                            "distance": distance,
                            "required": self.min_clearance
                        })                        
                    # Only show a few lines to avoid cluttering
                    if len(self.issues["insufficient_clearance"]) > 10:
                        break
            except Exception as e:
                print(f"Error checking clearances: {str(e)}")

    def _format_issue(self, issue_type, issue):
        """Format a specific issue for the report"""
        if issue_type == "wall thickness":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has wall thickness of {issue['thickness']:.2f}mm (conditions: {issue['required']}mm)"
        elif issue_type == "small_features":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has feature size of {issue['size']:.2f}mm (min: {issue['required']}mm)"
        elif issue_type == "overhangs":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has overhang angle of {issue['angle']:.2f}° (max: {issue['max_allowed']}°)"
        elif issue_type == "small_radius":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has hole diameter of {issue['diameter']:.2f}mm (min: {issue['required']}mm)"
        elif issue_type == "high_aspect_ratio":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has aspect ratio of {issue['aspect_ratio']:.2f} (max: {issue['max_allowed']})"
        elif issue_type == "insufficient_clearance":
            return f"Distance between '{issue['object1']}' and '{issue['object2']}' is {issue['distance']:.2f}mm (min: {issue['required']}mm)"
        else:
            return str(issue)


def run_dfm_checker(process_type="FDM"):
    """Run the DFM checker on the active document with the specified process type"""
    if not App.ActiveDocument:
        print("No active document. Please open or create a document first.")
        return
        
    checker = DFMChecker(process_type=process_type)
    issues = checker.run_all_checks()
    
    # Change to problem highlight view
    if any(issues.values()):
        Gui.ActiveDocument.activeView().viewAxonometric()
        Gui.SendMsgToActiveView("ViewFit")
    
    return issues


# Example usage:
# run_dfm_checker("FDM")  # For FDM printing
# run_dfm_checker("SLA")  # For SLA printing
# run_dfm_checker("SLS")  # For SLS printing


def run_tdp_dfm_checker(
    doc_name = None, 
    process_type="FDM", 
    min_wall_thickness=1.0, 
    min_feature_size=0.8,  
    max_overhang_angle=45.0, 
    min_hole_radius=1.0, 
    min_text_size=2.0,
    min_vertical_wire_thickness = 1.0,
    min_clearance = 0.5,
    max_aspect_ratio = 20
    ):
    """Run the 3D Printing DFM checker on the active document with the specified parameters"""
    print("3D Printing DFM check started.")
    if (not App.ActiveDocument) and (doc_name is None):
        print("No active document. Please open or create a document first.")
        return
        
    if doc_name is not None:
        doc = App.getDocument(doc_name)
    else:
        doc = None
        
    checker = TDPDFMChecker(
        doc=doc,
        process_type=process_type,
        min_wall_thickness=min_wall_thickness,
        min_feature_size=min_feature_size,
        max_overhang_angle=max_overhang_angle,
        min_hole_radius=min_hole_radius,
        min_text_size=min_text_size,
        min_vertical_wire_thickness=min_vertical_wire_thickness,
        min_clearance=min_clearance,
        max_aspect_ratio = max_aspect_ratio,
    )
    issues, report_text = checker.run_all_checks()
    
    # Change to problem highlight view
    if any(issues.values()) and App.GuiUp:
        Gui.ActiveDocument.activeView().viewAxonometric()
        Gui.SendMsgToActiveView("ViewFit")
    
    print("3D Printing DFM check completed.")
    return checker.success, issues, report_text, checker
    

# Add a simple UI to run the checks
if App.GuiUp:
    from PySide import QtCore, QtGui
    
    class TDPDFMCheckerDialog(QtGui.QDialog):
        def __init__(self):
            super(TDPDFMCheckerDialog, self).__init__()
            
            self.presets = {
                "Other": {
                    "min_wall_thickness": 1.0, 
                    "min_feature_size": 0.8,  
                    "max_overhang_angle": 45.0, 
                    "min_hole_radius": 2.0, 
                    "min_text_size": 2.0,
                    "min_clearance": 0.5,
                    "max_aspect_ratio": 20,
                },
                "FDM": {
                    "min_wall_thickness": 0.8,
                    "min_feature_size": 0.6,
                    "max_overhang_angle": 45.0,
                    "min_hole_radius": 1.0,
                    "min_text_size": 2.0,
                    "min_clearance": 0.5,
                    "max_aspect_ratio": 20,
                },
                "SLA": {
                    "min_wall_thickness": 0.5,
                    "min_feature_size": 0.3,
                    "max_overhang_angle": 30.0,
                    "min_hole_radius": 0.5,
                    "min_text_size": 1.0,
                    "min_clearance": 0.3,
                    "max_aspect_ratio": 30,
                },
                "SLS": {
                    "min_wall_thickness": 0.7,
                    "min_feature_size": 0.5,
                    "max_overhang_angle": 0.0,
                    "min_hole_radius": 0.75,
                    "min_text_size": 1.5,
                    "min_clearance": 0.5,
                    "max_aspect_ratio": 40,
                },
            }
            
            self.setWindowTitle("3D Printing DFM Checker")
            self.resize(300, 450)
            
            layout = QtGui.QVBoxLayout()

            # Parameter inputs
            form_layout = QtGui.QFormLayout()
            
            # Process selection
            self.internal_change = True
            
            self.prev_combo_item = "Other"
            self.process_label = QtGui.QLabel("Select 3D Printing Process:")
            self.process_combo = QtGui.QComboBox()
            self.process_combo.addItems(list(self.presets.keys()))
            self.set_combo_option(self.prev_combo_item)
            self.process_combo.currentIndexChanged.connect(self.on_combo_changed)
            
            self.wall_thickness_spin = QtGui.QDoubleSpinBox()
            self.wall_thickness_spin.setRange(0.1, 100.0)
            self.wall_thickness_spin.setSuffix(" mm")
            self.wall_thickness_spin.valueChanged.connect(self.on_value_changed)
            
            self.small_features_spin = QtGui.QDoubleSpinBox()
            self.small_features_spin.setRange(0.1, 100.0)
            self.small_features_spin.setSuffix(" mm")
            self.small_features_spin.valueChanged.connect(self.on_value_changed)
            
            self.overhang_angle_spin = QtGui.QDoubleSpinBox()
            self.overhang_angle_spin.setRange(0.1, 100.0)
            self.overhang_angle_spin.setSuffix(" degrees")
            self.overhang_angle_spin.valueChanged.connect(self.on_value_changed)
            
            self.small_hole_radius_spin = QtGui.QDoubleSpinBox()
            self.small_hole_radius_spin.setRange(0.1, 100.0)
            self.small_hole_radius_spin.setSuffix(" mm")
            self.small_hole_radius_spin.valueChanged.connect(self.on_value_changed)
            
            self.min_text_size_spin = QtGui.QDoubleSpinBox()
            self.min_text_size_spin.setRange(0.1, 100.0)
            self.min_text_size_spin.setSuffix(" mm")
            self.min_text_size_spin.valueChanged.connect(self.on_value_changed)
            
            self.min_clearance_spin = QtGui.QDoubleSpinBox()
            self.min_clearance_spin.setRange(0.1, 100.0)
            self.min_clearance_spin.setSuffix(" mm")
            self.min_clearance_spin.valueChanged.connect(self.on_value_changed)
            
            self.aspect_ratio_spin = QtGui.QDoubleSpinBox()
            self.aspect_ratio_spin.setRange(1.0, 100.0)
            self.aspect_ratio_spin.valueChanged.connect(self.on_value_changed)
            
            self.set_values_from_presets()
            self.internal_change = False
            
            form_layout.addRow("Min. Wall Thickness:", self.wall_thickness_spin)
            form_layout.addRow("Min. Features Size:", self.small_features_spin)
            form_layout.addRow("Max. Overhang Angle:", self.overhang_angle_spin)
            form_layout.addRow("Min. Hole Radius:", self.small_hole_radius_spin)
            form_layout.addRow("Min. Text Size:", self.min_text_size_spin)
            form_layout.addRow("Min. Clearance:", self.min_clearance_spin)
            form_layout.addRow("Max. Depth/Width Ratio:", self.aspect_ratio_spin)
            
            # Run button
            self.run_button = QtGui.QPushButton("Run 3D Printing DFM Check")
            self.run_button.clicked.connect(self.run_check)
            
            # Restore colors button
            self.restore_button = QtGui.QPushButton("Restore Original Colors")
            self.restore_button.clicked.connect(self.restore_colors)
            self.restore_button.setEnabled(False)
            
            # Status label
            self.status_label = QtGui.QLabel("Status: Ready")
            
            # Add widgets to layout
            layout.addWidget(self.process_label)
            layout.addWidget(self.process_combo)
            layout.addLayout(form_layout)
            layout.addWidget(self.run_button)
            layout.addWidget(self.restore_button)
            layout.addWidget(self.status_label)
            
            color_schemes = {
                "wall_thickness": (0.0, 1.0, 1.0),  # Cyan
                "small_features": (0.0, 1.0, 0.0),  # Green
                "overhangs": (1.0, 1.0, 0.0),  # Yellow
                "small_radius": (1.0, 0.5, 0.0),  # Orange
                "small_text": (1.0, 0.0, 0.0),  # Red
                "high_aspect_ratio": (0.0, 0.0, 1.0),  # Blue
                "insufficient_clearance": (1.0, 0.0, 1.0)  # Magenta
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
            
        def set_values_from_presets(self):
            process_type = self.process_combo.currentText()
            if (process_type not in self.presets):
                process_type = "Other"
            self.internal_change = True
            self.wall_thickness_spin.setValue(self.presets[process_type]["min_wall_thickness"])
            self.small_features_spin.setValue(self.presets[process_type]["min_feature_size"])
            self.overhang_angle_spin.setValue(self.presets[process_type]["max_overhang_angle"])
            self.small_hole_radius_spin.setValue(self.presets[process_type]["min_hole_radius"])
            self.min_text_size_spin.setValue(self.presets[process_type]["min_text_size"])
            self.min_clearance_spin.setValue(self.presets[process_type]["min_clearance"])
            self.aspect_ratio_spin.setValue(self.presets[process_type]["max_aspect_ratio"])
            self.internal_change = False
        
        def set_presets_values(self, process_type: str = "Other"):
            self.presets[process_type]["min_wall_thickness"] = self.wall_thickness_spin.value() 
            self.presets[process_type]["min_feature_size"]=self.small_features_spin.value()  
            self.presets[process_type]["max_overhang_angle"] = self.overhang_angle_spin.value() 
            self.presets[process_type]["min_hole_radius"] = self.small_hole_radius_spin.value() 
            self.presets[process_type]["min_text_size"] = self.min_text_size_spin.value()
            self.presets[process_type]["min_clearance"] = self.min_clearance_spin.value()
            self.presets[process_type]["max_aspect_ratio"] = self.aspect_ratio_spin.value()
            
        def set_combo_option(self, option: str) -> bool:
            index = self.process_combo.findText(option)
            if (index >= 0):
                self.process_combo.setCurrentIndex(index)
                return True
            return False
        
        def on_combo_changed(self, index):
            if self.prev_combo_item == "Other":
                self.set_presets_values()
            self.set_values_from_presets()
            self.prev_combo_item = self.process_combo.currentText()
            
        def on_value_changed(self, value):
            if not self.internal_change:
                process_type = self.process_combo.currentText()
                if process_type != "Other":
                    self.internal_change = True
                    self.set_presets_values()
                    self.set_combo_option("Other")
                    self.prev_combo_item = self.process_combo.currentText()
                    self.internal_change = False
        
        def run_check(self):
            self.status_label.setText("Status: Running CNC DFM checks...")
            
            # Run the checker
            try:
                # Restore colors from previous run if any
                if self.current_checker:
                    self.current_checker.restore_original_colors()
                    self.current_checker.remove_additional_objects()
                
                # Run the new check
                success, issues, report_text, checker = run_tdp_dfm_checker(
                    doc_name = None,
                    process_type = self.process_combo.currentText(),
                    min_wall_thickness=self.wall_thickness_spin.value(), 
                    min_feature_size=self.small_features_spin.value(),  
                    max_overhang_angle=self.overhang_angle_spin.value(), 
                    min_hole_radius=self.small_hole_radius_spin.value(), 
                    min_text_size=self.min_text_size_spin.value(),
                    min_vertical_wire_thickness = 1.0,
                    min_clearance = self.min_clearance_spin.value(),
                    max_aspect_ratio = self.aspect_ratio_spin.value(),
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

