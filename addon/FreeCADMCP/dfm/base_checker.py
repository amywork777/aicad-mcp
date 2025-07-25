import FreeCAD as App
import FreeCADGui as Gui
import Part
import math
import random
import os
from typing import Dict, Any

class DFMChecker:
    def __init__(self, doc=None, min_wall_thickness=1.0, max_wall_thickness=-1.0):
        """
        Initialize the base checker class.        
        Args:
            doc: FreeCAD document to check (defaults to active document)
        """
        self.doc = doc if doc else App.ActiveDocument
        # DFM rules
        self.min_wall_thickness = min_wall_thickness
        self.max_wall_thickness = max_wall_thickness  # < 0 for skipping this check
        # Dictionary to store issues
        self.issues = {
            "wall_thickness": [],
        }
        self.success = True        
        # Color schemes for highlighting issues
        self.color_schemes = {
            "wall_thickness": (0.0, 1.0, 1.0),  # Cyan
        }
        # Store original colors to restore later
        self.original_colors = {}
        # Storage for additional objects
        self.additional_objects = []
    
    def run_all_checks(self):
        """Run all CNC DFM checks on the document and highlight issues"""
        self.success = True
        print("Running DFM checks...")
        
        # Check each visible object in the document
        for obj in self.doc.Objects:
            if hasattr(obj, "Shape") and hasattr(obj, "ViewObject") and obj.ViewObject.Visibility:
                print(f"Checking object: {obj.Label}")             
                # Run all checks on this object
                try:
                    self.check_wall_thickness(obj)
                except Exception as e:
                    print(f"Check walls thickness error: {str(e)}")
                    self.success = False
        
        # Create summary report
        report_text = self.create_report()
        
        # Recompute document
        self.doc.recompute()
        print("DFM Analysis completed.")
        return self.issues, report_text
    
    def check_wall_thickness(self, obj):
        """
        Improved method to check for walls thinner than minimum thickness or thicker than maximum thickness
        Uses strategic sampling and optimization for better performance
        """
        print("Checking for wall thickness...")
        shape = obj.Shape
        
        # Get the bounding box of the shape
        bbox = shape.BoundBox
        bbox_diag = math.sqrt(bbox.DiagonalLength)
        
        # Create a set to track faces with thin walls
        problem_faces = set()
        
        # Process each face in the shape
        for face_idx, face in enumerate(shape.Faces):
            # print("Process", face_idx, "face.")
            face_checked = False
            # Skip very small faces to improve performance
            if face.Area < 0.01:
                continue
            
            # Sample strategic points on the face:
            # 1. Face center
            # print("Step1")
            try:
                center = face.Surface.parameter(face.CenterOfMass)
                normal = face.normalAt(center[0], center[1])
                # center_pt = App.Vector(center[0], center[1], 0.0)
                # center_pt = face.Surface.value(center[0], center[1])
                center_pt = face.Surface.value(center[0], center[1])                
                thickness = self.measure_wall_thickness(shape, center_pt, normal, bbox_diag)
                if thickness and ((thickness < self.min_wall_thickness) or ((self.max_wall_thickness > 0) and (thickness > self.max_wall_thickness))):
                    problem_faces.add(face)
                    self.issues["wall_thickness"].append({
                        "object": obj.Label,
                        "face": get_face_name(face, obj),
                        "location": f"Face center at {center}",
                        "thickness": thickness,
                        "required": f">self.min_wall_thickness" if self.max_wall_thickness <= 0 else f"> {self.min_wall_thickness} < {self.max_wall_thickness}"
                    })
                    face_checked = True                   
                    # Already found an issue on this face, no need to check more points
                    continue
            except Exception as e:
                print(f"Face center exception: {str(e)}")
                self.success = False
                # Skip if we can't get center or normal
            if face_checked:
                continue
            
            # 2. Sample points near edges (these are often trouble spots)
            # print("Step2")
            for edge in face.Edges:
                try:
                    # Sample middle of the edge
                    param = (edge.FirstParameter + edge.LastParameter) / 2
                    point = edge.valueAt(param)
                    projected_point = face.Surface.projectPoint(point)
                    u, v = face.Surface.parameter(projected_point)
                    # Get normal at this specific point
                    try:                        
                        normal = face.normalAt(u, v)
                    except Exception as e:
                        print(f"Edge point, normal calculation exception: {str(e)}")
                        # If parameter mapping fails, try using nearby point slightly offset from the surface
                        # This helps with numerical stability
                        local_normal = face.tangentAt(u, v)
                        point_offset = point.add(local_normal.multiply(0.001))
                        projected_point_offset = face.projectPoint(point_offset)
                        u, v = face.Surface.parameter(projected_point_offset)
                        # u, v = face.getParameterByPoint(point_offset)
                        normal = face.normalAt(u, v)                    
                    thickness = self.measure_wall_thickness(shape, point, normal, bbox_diag)
                    if thickness and ((thickness < self.min_wall_thickness) or ((self.max_wall_thickness > 0) and (thickness > self.max_wall_thickness))):
                        problem_faces.add(face)                        
                        self.issues["wall_thickness"].append({
                            "object": obj.Label,
                            "face": get_face_name(face, obj),
                            "location": f"Near edge at {point}",
                            "thickness": thickness,
                            "required": f">self.min_wall_thickness" if self.max_wall_thickness <= 0 else f"> {self.min_wall_thickness} < {self.max_wall_thickness}"
                        })                        
                        # Found an issue, no need to check more edges
                        face_checked = True
                        break
                except Exception as e:
                    print(f"Edge point exception: {str(e)}")
                    self.success = False
                    # Skip problematic edges
                    continue
            if face_checked:
                continue
                
            # 3. Sample vertices for corners (another common place for thin walls)
            # print("Step3")
            for vertex in face.Vertexes:
                try:
                    point = vertex.Point
                    projected_point = face.Surface.projectPoint(point)
                    u, v = face.Surface.parameter(projected_point)
                    # Get normal at this specific vertex
                    try:
                        normal = face.normalAt(u, v)
                    except Exception as e:
                        print(f"Vertex, normal calculation exception: {str(e)}")
                        # For vertices, if parameter mapping fails, use a slightly offset point
                        # Move slightly inward from the vertex
                        center = face.Surface.parameter(face.CenterOfMass)
                        center_pt = App.Vector(center[0], center[1], 0.0)
                        projected_pt = App.Vector(u, v, 0.0)
                        center_vector = center_pt.sub(point)
                        center_vector.normalize()
                        projected_pt.add(center_vector.multiply(0.001))
                        u = projected_pt.x
                        v = projected_pt.y
                        normal = face.normalAt(u, v)                    
                    thickness = self.measure_wall_thickness(shape, point, normal, bbox_diag)
                    if thickness and ((thickness < self.min_wall_thickness) or ((self.max_wall_thickness > 0) and (thickness > self.max_wall_thickness))):
                        problem_faces.add(face)
                        self.issues["wall_thickness"].append({
                            "object": obj.Label,
                            "face": get_face_name(face, obj),
                            "location": f"Near vertex at {point}",
                            "thickness": thickness,
                            "required": f">self.min_wall_thickness" if self.max_wall_thickness <= 0 else f"> {self.min_wall_thickness} < {self.max_wall_thickness}"
                        })
                        face_checked = True                        
                        # Found an issue, no need to check more vertices
                        break
                except Exception as e:
                    print(f"Vertex exception: {str(e)}")
                    self.success = False
                    continue
            if face_checked:
                continue
            
            # 4. Fixed grid in UV plane
            # print("Step4")
            grid_steps = 3
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
                for uidx in range(1, u_steps):
                    cur_u = u_min + uidx * u_step
                    for vidx in range(1, v_steps):
                        cur_v = v_min + vidx * v_step
                        normal = face.normalAt(cur_u, cur_v)
                        pt = face.Surface.value(cur_u, cur_v)
                        thickness = self.measure_wall_thickness(shape, pt, normal, bbox_diag)
                        if thickness and ((thickness < self.min_wall_thickness) or ((self.max_wall_thickness > 0) and (thickness > self.max_wall_thickness))):
                            problem_faces.add(face)                   
                            self.issues["wall_thickness"].append({
                                "object": obj.Label,
                                "face": get_face_name(face, obj),
                                "location": f"Face center at {center}",
                                "thickness": thickness,
                                "required": f">self.min_wall_thickness" if self.max_wall_thickness <= 0 else f"> {self.min_wall_thickness} < {self.max_wall_thickness}"
                            })
                            face_checked = True                    
                            # Already found an issue on this face, no need to check more points
                            continue
            except Exception as e:
                print(f"Face grid exception: {str(e)}")
                self.success = False
                # Skip if we can't get center or normal
                    
        # Highlight all faces that are part of thin walls
        for face in problem_faces:
            self.highlight_feature(face, obj, "WallThickness", "wall_thickness")
    
    def measure_wall_thickness(self, shape, point, normal, bbox_diag=None):
        """
        Improved method to measure wall thickness using ray casting
        with optimizations for performance and accuracy
        
        Args:
            shape: The shape to check
            point: The starting point for measurement (on surface)
            normal: The normal direction at the point
            bbox_diag: The diagonal length of the bounding box (for optimization)
            
        Returns:
            The wall thickness at the given point, or None if no valid measurement
        """
        min_threshold = 0.001
        # print("Measuring wall thickness.")
        # If bbox_diag is not provided, calculate it
        if bbox_diag is None:
            bbox_diag = shape.BoundBox.DiagonalLength
        
        # Use bounding box diagonal as maximum ray length
        max_ray_length = min(bbox_diag, 1000)  # Cap at 1000mm for very large models
        
        # For a point on the surface, we need to cast rays in both positive and 
        # negative normal directions
        try:
            ray_pos = Part.Line(point, point.add(normal.multiply(max_ray_length)))
            ray_neg = Part.Line(point, point.add(normal.multiply(-max_ray_length)))
        except Exception as e:
            print(f"Measure wall thickness - line: {str(e)}")
            return None
        
        # Get intersections
        try:
            intersections_pos = shape.section([ray_pos]).Vertexes
            intersections_neg = shape.section([ray_neg]).Vertexes
        except Exception as e:
            print(f"Measure wall thickness - intersection: {str(e)}")
            # Ray casting failed
            return None
        
        # Filter out the starting point (which might be counted as an intersection)
        # Use a small tolerance to avoid numerical issues
        tol = 0.005  # 0.005mm tolerance
        intersections_pos = [v for v in intersections_pos if v.Point.distanceToPoint(point) > tol]
        intersections_neg = [v for v in intersections_neg if v.Point.distanceToPoint(point) > tol]
        
        # If the point is on the surface, one direction should at least have intersections
        # The other direction might not have intersections if it's a one-sided wall
        # if not intersections_pos and not intersections_neg:
        #     return None
        
        # This is a robust soution by CAI that considers the points inside or outside the object
        # For surface points, calculate differently from internal points:
        # 1. If both directions have intersections, calculate the minimum total distance
        # if intersections_pos and intersections_neg:
        #     min_dist_pos = min([point.distanceToPoint(v.Point) for v in intersections_pos])
        #     min_dist_neg = min([point.distanceToPoint(v.Point) for v in intersections_neg])
        #     thickness = min_dist_pos + min_dist_neg
        # 2. If only one direction has intersections, find the two closest intersections
        # elif intersections_pos:
        #     # Sort distances from smallest to largest
        #     distances = sorted([point.distanceToPoint(v.Point) for v in intersections_pos])
        #     # Need at least two intersections to measure thickness
        #     if len(distances) < 2:
        #         return None
        #     # Thickness is distance between first two intersections
        #     thickness = distances[1] - distances[0]
        # elif intersections_neg:
        #     # Same logic for negative direction
        #     distances = sorted([point.distanceToPoint(v.Point) for v in intersections_neg])
        #     if len(distances) < 2:
        #         return None
        #     thickness = distances[1] - distances[0]
        # else:
        #     # This shouldn't happen due to earlier check, but just in case
        #     return None
        # print("Len pos = ", len(intersections_pos), " Len neg = ", len(intersections_neg))
        # print("Intersections pos = ", intersections_pos)
        # print("Intersections neg = ", intersections_neg)
        
        # This is a custom solution that considers, that all the points
        thickness = 0        
        if intersections_pos:
            min_dist_pos = min([point.distanceToPoint(v.Point) for v in intersections_pos])
            if (min_dist_pos <= min_threshold) and (len(intersections_pos) > 1):
                distances = sorted([point.distanceToPoint(v.Point) for v in intersections_pos])
                min_dist_pos = distances[1]
            if intersections_neg:
                min_dist_neg = min([point.distanceToPoint(v.Point) for v in intersections_neg])
                if (min_dist_neg <= min_threshold) and (len(intersections_neg) > 0):
                    distances = sorted([point.distanceToPoint(v.Point) for v in intersections_neg])
                    min_dist_neg = distances[1]
                thickness = min(min_dist_pos, min_dist_neg)
                if thickness <= min_threshold:
                    thickness = max(min_dist_pos, min_dist_neg)
            else:
                thickness = min_dist_pos
        elif intersections_neg:
            min_dist_neg = min([point.distanceToPoint(v.Point) for v in intersections_neg])
            if (min_dist_neg <= min_threshold) and (len(intersections_neg) > 0):
                distances = sorted([point.distanceToPoint(v.Point) for v in intersections_neg])
                min_dist_neg = distances[1]
            thickness = min_dist_neg
        # print("Thickness = ", thickness)
        
        # Verify this looks reasonable (sanity check)
        if thickness > bbox_diag or thickness < 0.01:
            return None
        
        return thickness
    
    def highlight_feature(self, shape_object, parent_obj, issue_type, color_key):
        """
        Highlight a problematic feature by changing the color of the original object
    
        Args:
            shape_object: The shape object (edge, face, etc.) to highlight
            parent_obj: The parent object containing the shape
            issue_type: Type of issue being highlighted
            color_key: Key to the color scheme
        """
        # Store original color if we haven't seen this object yet
        if parent_obj.Name not in self.original_colors:
            # Create a deep copy of the DiffuseColor to avoid reference issues
            diffuse_color = None
            if hasattr(parent_obj.ViewObject, "DiffuseColor"):
                if isinstance(parent_obj.ViewObject.DiffuseColor, list):
                    diffuse_color = list(parent_obj.ViewObject.DiffuseColor)
                else:
                    diffuse_color = parent_obj.ViewObject.DiffuseColor

            self.original_colors[parent_obj.Name] = {
                "shape_color": parent_obj.ViewObject.ShapeColor,
                "diffuse_color": diffuse_color,
                "line_color": parent_obj.ViewObject.LineColor,
                "line_width": parent_obj.ViewObject.LineWidth,
                "shape_color_affected": False,
                "diffuse_color_affected": False,
                "line_color_affected": False,
                "line_width_affected": False,
                "face_count": len(parent_obj.Shape.Faces) if hasattr(parent_obj.Shape, "Faces") else 0
            }
    
        # Apply the highlighting color
        color = self.color_schemes[color_key]
    
        # Apply color to face or subshape
        if isinstance(shape_object, Part.Face):
            # Handle face coloring
            colors = parent_obj.ViewObject.DiffuseColor
        
            # If colors array isn't per-face yet, expand it
            if (colors is None) or (not isinstance(colors, list)) or (len(colors) != len(parent_obj.Shape.Faces)):
                base_color = parent_obj.ViewObject.ShapeColor
                if colors is not None and isinstance(colors, list) and len(colors) > 0:
                    try:
                        base_color = colors[0]
                    except:
                        pass
                colors = [base_color] * len(parent_obj.Shape.Faces)
        
            # Find the index of this face in the parent shape
            for i, face in enumerate(parent_obj.Shape.Faces):
                if face.isSame(shape_object):
                    colors[i] = color
                    break
        
            # Apply the updated colors
            parent_obj.ViewObject.DiffuseColor = colors
            self.original_colors[parent_obj.Name]["diffuse_color_affected"] = True
        
        # Rest of the method remains the same
        elif isinstance(shape_object, Part.Edge):
            # For edges, we'll need to handle differently - use line color/width
            parent_obj.ViewObject.LineColor = color
            parent_obj.ViewObject.LineWidth = 5
            self.original_colors[parent_obj.Name]["line_color_affected"] = True
            self.original_colors[parent_obj.Name]["line_width_affected"] = True
        
        # Other cases remain the same...
        elif isinstance(shape_object, list):
            # Handle lists of shapes (like multiple edges)
            if all(isinstance(item, Part.Edge) for item in shape_object):
                # All edges - set line color
                parent_obj.ViewObject.LineColor = color
                parent_obj.ViewObject.LineWidth = 5
                self.original_colors[parent_obj.Name]["line_color_affected"] = True
                self.original_colors[parent_obj.Name]["line_width_affected"] = True
            elif all(isinstance(item, Part.Face) for item in shape_object):
                # All faces - set diffuse color for each face
                colors = parent_obj.ViewObject.DiffuseColor                
                # If colors array isn't per-face yet, expand it
                if (colors is None) or (not isinstance(colors, list)) or (len(colors) != len(parent_obj.Shape.Faces)):
                    if colors is None:
                        base_color = parent_obj.ViewObject.ShapeColor
                    else:
                        try:
                            base_color = colors[0]
                        except:
                            base_color = colors
                    colors = [base_color] * len(parent_obj.Shape.Faces)
                # Find and color each face
                for face_to_highlight in shape_object:
                    for i, face in enumerate(parent_obj.Shape.Faces):
                        if face.isSame(face_to_highlight):
                            colors[i] = color
                            break                
                # Apply the updated colors
                parent_obj.ViewObject.DiffuseColor = colors
                self.original_colors[parent_obj.Name]["diffuse_color_affected"] = True
            else:
                # Mixed or unknown types - just color the whole object
                parent_obj.ViewObject.ShapeColor = color
                self.original_colors[parent_obj.Name]["shape_color_affected"] = True
            
        else:
            # Unknown shape type - just color the whole object
            parent_obj.ViewObject.ShapeColor = color
            self.original_colors[parent_obj.Name]["shape_color_affected"] = True

    def restore_original_colors(self):
        """Restore the original colors of all highlighted objects"""
        try:
            restore_original_colors(self.doc.Name, self.original_colors)
            # Clear the storage
            self.original_colors = {}
        except Exception as e:
            print(f"Restoring original colors: {str(e)}")
            
    def remove_additional_objects(self):
        try:
            remove_additional_objects(self.doc.Name, self.additional_objects)
            self.additional_objects = []
        except Exception as e:
            print(f"Removing additional objects: {str(e)}")
    
    def create_report(self, base_text: str = "DFM Issues Report"):
        """Create a report of all DFM issues found"""
        report = []
        report.append(base_text)
        report.append("=" * 40)
        
        # Summarize all issues
        total_issues = sum(len(issues) for issues in self.issues.values())
        if total_issues == 0:
            report.append("No DFM issues found! The model appears to be machinable.")
        else:
            report.append(f"Found {total_issues} potential issues:")
            
            for issue_type, issues in self.issues.items():
                if not issues:
                    continue
                if not isinstance(issues, list):
                    continue
                    
                issue_name = issue_type.replace("_", " ").title()
                report.append(f"\n{issue_name} ({len(issues)}):")
                
                for i, issue in enumerate(issues):
                    report.append(f"  {i+1}. {self.format_issue(issue_type, issue)}")
            
            report.append(f"Success: {self.success}")
            # report.append("\nRecommendations:")
            # report.append("-" * 20)
            # report.append("1. Ensure all internal corners have a radius of at least the tool radius")
            # report.append("2. Avoid features smaller than the smallest available tool")
            # report.append("3. Keep depth to width ratio under 4:1 for pockets and holes")
            # report.append("4. Maintain wall thickness appropriate for material (typically >1mm)")
            # report.append("5. Consider the approach vector for the tool - vertical walls may be difficult to machine")
            # report.append("6. Avoid deep narrow channels that may cause tool deflection")
        
        # Print to console
        print("\n".join(report))
        
        # Create a text file in the document
        try:
            report_text = "\n".join(report)
            with open(os.path.join(App.getUserAppDataDir(), "CNC_DFM_Report.txt"), "w") as report_file:
                report_file.write(report_text)
            import json
            with open(os.path.join(App.getUserAppDataDir(), "CNC_DFM_Report.json"), "w") as report_file:
                json.dump({"success": self.success, "issues": self.issues}, report_file, indent=4)
            print(f"Report saved to: {App.getUserAppDataDir()}/CNC_DFM_Report.txt")
        except Exception as e:
            report_text = None
            print(f"Could not create report file: {str(e)}")
        
        # Create a text document in FreeCAD
        try:
            report_obj = self.doc.addObject("App::TextDocument", "CNC_DFM_Report")
            report_obj.Text = report_text
            self.doc.recompute()
        except Exception as e:
            print(f"Could not create report document in FreeCAD: {str(e)}")
        return report_text
    
    def format_issue(self, issue_type, issue):
        """Format a specific issue for the report"""
        if issue_type == "wall_thickness":
            return f"Face '{issue['face']}' in object '{issue['object']}' at {issue['location']} has wall thickness of {issue['thickness']:.2f}mm (conditions: {issue['required']}mm)"
        else:
            return str(issue)


def get_face_name(face, obj):
    """
    Get the face name (e.g., "Face33") for a given face in an object.
    
    Parameters:
    face (Part.Face): The face to get the name for
    obj (App.DocumentObject): The object containing the face
    
    Returns:
    str: The face name in the format "Face33"
    """
    for i, obj_face in enumerate(obj.Shape.Faces):
        if face.isSame(obj_face):
            return f"Face{i+1}"  # +1 because FreeCAD UI uses 1-based indexing   
    return None  # Face not found in the object


def run_dfm_checker(doc_name = None, min_wall_thickness=1.0):
    """Run the DFM checker on the active document with the specified parameters"""
    print("DFM check started.")
    if (not App.ActiveDocument) and (doc_name is None):
        print("No active document. Please open or create a document first.")
        return
        
    if doc_name is not None:
        doc = App.getDocument(doc_name)
    else:
        doc = None
        
    checker = DFMChecker(
        doc=doc,
        min_wall_thickness=min_wall_thickness
    )
    issues, report_text = checker.run_all_checks()
    
    # Change to problem highlight view
    if any(issues.values()) and App.GuiUp:
        Gui.ActiveDocument.activeView().viewAxonometric()
        Gui.SendMsgToActiveView("ViewFit")
    
    print("DFM check completed.")
    return checker.success, issues, report_text, checker
    

def restore_original_colors(doc_name, original_colors: Dict[str, Any]) -> str:
        """Restore the original colors of all highlighted objects"""
        try:
            doc = App.getDocument(doc_name)
            if not doc:
                return "Document not found."
            for obj_name, entry in original_colors.items():
                try:
                    obj = doc.getObject(obj_name)
                    if not obj or not hasattr(obj, "ViewObject"):
                        continue
                    else:
                        # Only restore properties that were affected
                        if entry.get("shape_color_affected", False):
                            obj.ViewObject.ShapeColor = entry["shape_color"]
            
                        # For DiffuseColor, we need special handling
                        if entry.get("diffuse_color_affected", False):
                            # Check if the object still has the same number of faces
                            current_face_count = len(obj.Shape.Faces) if hasattr(obj.Shape, "Faces") else 0
                            original_face_count = entry["face_count"]
                
                            if current_face_count == original_face_count and entry["diffuse_color"] is not None:
                                # If same face count, we can restore the original colors
                                obj.ViewObject.DiffuseColor = entry["diffuse_color"]
                            else:
                                # If face count changed or we don't have original colors, reset to ShapeColor
                                if hasattr(obj.ViewObject, "DiffuseColor"):
                                    obj.ViewObject.DiffuseColor = []  # This will reset to ShapeColor in FreeCAD
            
                        # Reset line properties
                        if entry["line_color_affected"]:
                            obj.ViewObject.LineColor = entry["line_color"]
                        if entry["line_width_affected"]:
                            obj.ViewObject.LineWidth = entry["line_width"]
                except Exception as e:
                    return print(f"Error (object processing) restoring colors for {obj_name}: {str(e)}")
            doc.recompute()
            gui_available = Gui.getDocument(doc_name) is not None
            if gui_available:
                Gui.updateGui()
            return ""
        except Exception as e:
            return f"Error (global) restoring colors: {str(e)}"

            
def remove_additional_objects(doc_name, object_names):
    """
    Remove objects with specified names from a FreeCAD document.  
    Args:
        doc_name (str): The name of the document containing the objects to remove.
        object_names (list): List of object names to be removed from the document.    
    Returns:
        str - Result message.
    """
    # Try to get the document
    try:
        doc = App.getDocument(doc_name)
    except:
        return f"Document '{doc_name}' not found."
    # Keep track of successfully removed objects
    removed_objects = []
    failed_objects = []
    # Iterate through the list of object names
    for obj_name in object_names:
        try:
            # Check if the object exists in the document
            if doc.getObject(obj_name):
                # Remove the object
                doc.removeObject(obj_name)
                removed_objects.append(obj_name)
            else:
                failed_objects.append(obj_name)
        except Exception as e:
            failed_objects.append(f"{obj_name}+(Error: {str(e)})")
    # Recompute the document to update it
    doc.recompute()
    gui_available = Gui.getDocument(doc_name) is not None
    if gui_available:
        Gui.updateGui()
    # Create a summary message
    message = f"Removed {len(removed_objects)} objects from document '{doc_name}'."
    if removed_objects:
        message += f"\nRemoved objects: {', '.join(removed_objects)}"
    if failed_objects:
        message += f"\nFailed to remove objects: {', '.join(failed_objects)}"
    if len(failed_objects) == 0:
        return ""
    return message


# Add a simple UI to run the checks
if App.GuiUp:
    from PySide import QtCore, QtGui
    
    class DFMCheckerDialog(QtGui.QDialog):
        def __init__(self):
            super(DFMCheckerDialog, self).__init__()
            self.setWindowTitle("CNC Machining DFM Checker")
            self.resize(350, 200)
            
            layout = QtGui.QVBoxLayout()
            
            # Parameter inputs
            form_layout = QtGui.QFormLayout()
            
            self.wall_thickness_spin = QtGui.QDoubleSpinBox()
            self.wall_thickness_spin.setRange(0.1, 100.0)
            self.wall_thickness_spin.setValue(1.0)
            self.wall_thickness_spin.setSuffix(" mm")
            
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
                success, issues, report_text, checker = run_dfm_checker(
                    doc_name = None,
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

