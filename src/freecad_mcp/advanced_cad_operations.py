"""
Advanced CAD Operations Framework for FreeCAD
Provides feature-based modeling, parametric operations, and manufacturing-aware design tools.
"""

import math
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class FeatureType(Enum):
    """Types of CAD features"""
    SKETCH = "sketch"
    EXTRUDE = "extrude"
    REVOLVE = "revolve"
    SWEEP = "sweep"
    LOFT = "loft"
    FILLET = "fillet"
    CHAMFER = "chamfer"
    HOLE = "hole"
    POCKET = "pocket"
    RIB = "rib"
    SHELL = "shell"
    PATTERN = "pattern"
    BOOLEAN = "boolean"

class PatternType(Enum):
    """Types of patterns"""
    LINEAR = "linear"
    CIRCULAR = "circular"
    RECTANGULAR = "rectangular"
    PATH = "path"

class BooleanOperation(Enum):
    """Boolean operations"""
    UNION = "union"
    SUBTRACT = "subtract"
    INTERSECT = "intersect"

@dataclass
class ParametricExpression:
    """Parametric expression for dimensions"""
    expression: str
    variables: Dict[str, float]
    
    def evaluate(self) -> float:
        """Evaluate the parametric expression"""
        try:
            # Simple expression evaluator (in real implementation, use proper parser)
            result = eval(self.expression, {"__builtins__": {}}, self.variables)
            return float(result)
        except Exception as e:
            logger.error(f"Failed to evaluate expression '{self.expression}': {e}")
            return 0.0

@dataclass
class SketchConstraint:
    """Geometric constraint in a sketch"""
    constraint_type: str  # coincident, parallel, perpendicular, equal, distance, angle
    elements: List[str]   # Referenced sketch elements
    value: Optional[float] = None  # For dimensional constraints
    
@dataclass
class SketchElement:
    """Element in a parametric sketch"""
    element_type: str  # line, arc, circle, spline
    points: List[Tuple[float, float]]
    parameters: Dict[str, Any]
    constraints: List[SketchConstraint] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []

@dataclass
class ParametricSketch:
    """Parametric sketch with constraints and elements"""
    name: str
    plane: str  # XY, XZ, YZ, or custom
    elements: List[SketchElement]
    constraints: List[SketchConstraint]
    variables: Dict[str, float]
    
    def __post_init__(self):
        if not self.elements:
            self.elements = []
        if not self.constraints:
            self.constraints = []
        if not self.variables:
            self.variables = {}

@dataclass
class CADFeature:
    """Parametric CAD feature"""
    name: str
    feature_type: FeatureType
    parameters: Dict[str, Any]
    dependencies: List[str] = None  # Names of features this depends on
    sketch_name: Optional[str] = None
    manufacturing_notes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.manufacturing_notes is None:
            self.manufacturing_notes = {}

@dataclass
class AssemblyConstraint:
    """Constraint between assembly components"""
    constraint_type: str  # mate, align, insert, tangent
    component1: str
    component2: str
    element1: str  # Face, edge, or vertex reference
    element2: str
    offset: float = 0.0
    angle: float = 0.0

@dataclass
class AssemblyComponent:
    """Component in an assembly"""
    name: str
    file_path: str
    position: Tuple[float, float, float] = (0, 0, 0)
    rotation: Tuple[float, float, float] = (0, 0, 0)
    constraints: List[AssemblyConstraint] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []

class AdvancedCADOperations:
    """Advanced CAD operations with parametric and manufacturing capabilities"""
    
    def __init__(self):
        self.sketches: Dict[str, ParametricSketch] = {}
        self.features: Dict[str, CADFeature] = {}
        self.assemblies: Dict[str, List[AssemblyComponent]] = {}
        self.global_variables: Dict[str, float] = {}
        self.feature_tree: List[str] = []  # Ordered list of feature names
        
    def create_parametric_sketch(self, name: str, plane: str = "XY") -> ParametricSketch:
        """Create a new parametric sketch"""
        try:
            sketch = ParametricSketch(
                name=name,
                plane=plane,
                elements=[],
                constraints=[],
                variables={}
            )
            
            self.sketches[name] = sketch
            logger.info(f"Created parametric sketch: {name} on {plane} plane")
            return sketch
            
        except Exception as e:
            logger.error(f"Failed to create sketch {name}: {e}")
            raise
    
    def add_sketch_line(self, sketch_name: str, start: Tuple[float, float], 
                       end: Tuple[float, float], name: str = None) -> bool:
        """Add a line to a parametric sketch"""
        try:
            if sketch_name not in self.sketches:
                logger.error(f"Sketch {sketch_name} not found")
                return False
            
            element_name = name or f"Line_{len(self.sketches[sketch_name].elements)}"
            
            line_element = SketchElement(
                element_type="line",
                points=[start, end],
                parameters={
                    "name": element_name,
                    "length": math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                }
            )
            
            self.sketches[sketch_name].elements.append(line_element)
            logger.info(f"Added line {element_name} to sketch {sketch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add line to sketch {sketch_name}: {e}")
            return False
    
    def add_sketch_circle(self, sketch_name: str, center: Tuple[float, float], 
                         radius: float, name: str = None) -> bool:
        """Add a circle to a parametric sketch"""
        try:
            if sketch_name not in self.sketches:
                logger.error(f"Sketch {sketch_name} not found")
                return False
            
            element_name = name or f"Circle_{len(self.sketches[sketch_name].elements)}"
            
            circle_element = SketchElement(
                element_type="circle",
                points=[center],
                parameters={
                    "name": element_name,
                    "radius": radius,
                    "diameter": radius * 2
                }
            )
            
            self.sketches[sketch_name].elements.append(circle_element)
            logger.info(f"Added circle {element_name} to sketch {sketch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add circle to sketch {sketch_name}: {e}")
            return False
    
    def add_sketch_constraint(self, sketch_name: str, constraint: SketchConstraint) -> bool:
        """Add a geometric constraint to a sketch"""
        try:
            if sketch_name not in self.sketches:
                logger.error(f"Sketch {sketch_name} not found")
                return False
            
            self.sketches[sketch_name].constraints.append(constraint)
            logger.info(f"Added {constraint.constraint_type} constraint to sketch {sketch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add constraint to sketch {sketch_name}: {e}")
            return False
    
    def create_extrude_feature(self, name: str, sketch_name: str, length: Union[float, str],
                              direction: str = "normal", symmetric: bool = False) -> bool:
        """Create an extrude feature from a sketch"""
        try:
            if sketch_name not in self.sketches:
                logger.error(f"Sketch {sketch_name} not found")
                return False
            
            # Handle parametric length
            if isinstance(length, str):
                length_expr = ParametricExpression(length, self.global_variables)
                actual_length = length_expr.evaluate()
            else:
                actual_length = length
            
            feature = CADFeature(
                name=name,
                feature_type=FeatureType.EXTRUDE,
                parameters={
                    "length": actual_length,
                    "direction": direction,
                    "symmetric": symmetric,
                    "length_expression": length if isinstance(length, str) else None
                },
                dependencies=[],
                sketch_name=sketch_name,
                manufacturing_notes={
                    "process_hint": "suitable_for_milling",
                    "draft_angle": 0.5 if direction == "normal" else 0.0
                }
            )
            
            self.features[name] = feature
            self.feature_tree.append(name)
            logger.info(f"Created extrude feature: {name} from sketch {sketch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create extrude feature {name}: {e}")
            return False
    
    def create_revolve_feature(self, name: str, sketch_name: str, axis_point: Tuple[float, float],
                              axis_direction: Tuple[float, float], angle: Union[float, str] = 360.0) -> bool:
        """Create a revolve feature from a sketch"""
        try:
            if sketch_name not in self.sketches:
                logger.error(f"Sketch {sketch_name} not found")
                return False
            
            # Handle parametric angle
            if isinstance(angle, str):
                angle_expr = ParametricExpression(angle, self.global_variables)
                actual_angle = angle_expr.evaluate()
            else:
                actual_angle = angle
            
            feature = CADFeature(
                name=name,
                feature_type=FeatureType.REVOLVE,
                parameters={
                    "angle": actual_angle,
                    "axis_point": axis_point,
                    "axis_direction": axis_direction,
                    "angle_expression": angle if isinstance(angle, str) else None
                },
                dependencies=[],
                sketch_name=sketch_name,
                manufacturing_notes={
                    "process_hint": "suitable_for_turning",
                    "surface_finish": "Ra 1.6"
                }
            )
            
            self.features[name] = feature
            self.feature_tree.append(name)
            logger.info(f"Created revolve feature: {name} from sketch {sketch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create revolve feature {name}: {e}")
            return False
    
    def create_fillet_feature(self, name: str, edges: List[str], radius: Union[float, str]) -> bool:
        """Create a fillet feature on specified edges"""
        try:
            # Handle parametric radius
            if isinstance(radius, str):
                radius_expr = ParametricExpression(radius, self.global_variables)
                actual_radius = radius_expr.evaluate()
            else:
                actual_radius = radius
            
            feature = CADFeature(
                name=name,
                feature_type=FeatureType.FILLET,
                parameters={
                    "radius": actual_radius,
                    "edges": edges,
                    "radius_expression": radius if isinstance(radius, str) else None
                },
                dependencies=self._get_dependencies_for_edges(edges),
                manufacturing_notes={
                    "process_hint": "improves_stress_concentration",
                    "surface_finish": "Ra 0.8",
                    "tool_access": "required"
                }
            )
            
            self.features[name] = feature
            self.feature_tree.append(name)
            logger.info(f"Created fillet feature: {name} with radius {actual_radius}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create fillet feature {name}: {e}")
            return False
    
    def create_hole_feature(self, name: str, position: Tuple[float, float, float],
                           diameter: Union[float, str], depth: Union[float, str],
                           hole_type: str = "simple") -> bool:
        """Create a parametric hole feature"""
        try:
            # Handle parametric dimensions
            if isinstance(diameter, str):
                dia_expr = ParametricExpression(diameter, self.global_variables)
                actual_diameter = dia_expr.evaluate()
            else:
                actual_diameter = diameter
                
            if isinstance(depth, str):
                depth_expr = ParametricExpression(depth, self.global_variables)
                actual_depth = depth_expr.evaluate()
            else:
                actual_depth = depth
            
            # Manufacturing recommendations based on hole type
            manufacturing_notes = {
                "process_hint": "drill_operation",
                "aspect_ratio": actual_depth / actual_diameter,
                "tolerance": "H7" if hole_type == "precision" else "H9"
            }
            
            if manufacturing_notes["aspect_ratio"] > 5:
                manufacturing_notes["warning"] = "high_aspect_ratio_hole"
                manufacturing_notes["recommendation"] = "consider_stepped_drill"
            
            feature = CADFeature(
                name=name,
                feature_type=FeatureType.HOLE,
                parameters={
                    "position": position,
                    "diameter": actual_diameter,
                    "depth": actual_depth,
                    "hole_type": hole_type,
                    "diameter_expression": diameter if isinstance(diameter, str) else None,
                    "depth_expression": depth if isinstance(depth, str) else None
                },
                dependencies=[],
                manufacturing_notes=manufacturing_notes
            )
            
            self.features[name] = feature
            self.feature_tree.append(name)
            logger.info(f"Created hole feature: {name} - ∅{actual_diameter} × {actual_depth}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create hole feature {name}: {e}")
            return False
    
    def create_pattern_feature(self, name: str, base_feature: str, pattern_type: PatternType,
                              parameters: Dict[str, Any]) -> bool:
        """Create a pattern feature"""
        try:
            if base_feature not in self.features:
                logger.error(f"Base feature {base_feature} not found")
                return False
            
            pattern_params = parameters.copy()
            pattern_params["pattern_type"] = pattern_type.value
            pattern_params["base_feature"] = base_feature
            
            feature = CADFeature(
                name=name,
                feature_type=FeatureType.PATTERN,
                parameters=pattern_params,
                dependencies=[base_feature],
                manufacturing_notes={
                    "process_hint": "batch_operation",
                    "setup_time": "optimized_for_pattern"
                }
            )
            
            self.features[name] = feature
            self.feature_tree.append(name)
            logger.info(f"Created {pattern_type.value} pattern: {name} based on {base_feature}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create pattern feature {name}: {e}")
            return False
    
    def create_boolean_feature(self, name: str, operation: BooleanOperation,
                              target_features: List[str], tool_features: List[str]) -> bool:
        """Create a boolean operation feature"""
        try:
            # Validate that all referenced features exist
            all_features = target_features + tool_features
            for feature_name in all_features:
                if feature_name not in self.features:
                    logger.error(f"Feature {feature_name} not found")
                    return False
            
            feature = CADFeature(
                name=name,
                feature_type=FeatureType.BOOLEAN,
                parameters={
                    "operation": operation.value,
                    "target_features": target_features,
                    "tool_features": tool_features
                },
                dependencies=all_features,
                manufacturing_notes={
                    "process_hint": "complex_geometry",
                    "verification": "required"
                }
            )
            
            self.features[name] = feature
            self.feature_tree.append(name)
            logger.info(f"Created boolean {operation.value} feature: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create boolean feature {name}: {e}")
            return False
    
    def set_global_variable(self, name: str, value: float) -> bool:
        """Set a global parametric variable"""
        try:
            self.global_variables[name] = value
            logger.info(f"Set global variable {name} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set global variable {name}: {e}")
            return False
    
    def update_parametric_model(self) -> Dict[str, Any]:
        """Update the parametric model by recalculating all features"""
        results = {
            "updated_features": [],
            "errors": [],
            "warnings": []
        }
        
        try:
            # Update features in dependency order
            for feature_name in self.feature_tree:
                feature = self.features[feature_name]
                
                try:
                    # Update parametric expressions
                    updated_params = {}
                    for param_name, param_value in feature.parameters.items():
                        if param_name.endswith("_expression") and param_value:
                            expr = ParametricExpression(param_value, self.global_variables)
                            base_param = param_name.replace("_expression", "")
                            updated_params[base_param] = expr.evaluate()
                    
                    # Update feature parameters
                    feature.parameters.update(updated_params)
                    results["updated_features"].append(feature_name)
                    
                except Exception as e:
                    results["errors"].append(f"Failed to update feature {feature_name}: {e}")
            
            logger.info(f"Parametric model update complete: {len(results['updated_features'])} features updated")
            
        except Exception as e:
            logger.error(f"Parametric model update failed: {e}")
            results["errors"].append(f"Model update failed: {e}")
        
        return results
    
    def analyze_feature_dependencies(self) -> Dict[str, Any]:
        """Analyze feature dependencies and detect circular references"""
        analysis = {
            "dependency_graph": {},
            "circular_references": [],
            "orphaned_features": [],
            "dependency_depth": {}
        }
        
        try:
            # Build dependency graph
            for feature_name, feature in self.features.items():
                analysis["dependency_graph"][feature_name] = feature.dependencies
            
            # Check for circular references using DFS
            def has_circular_ref(node, visited, rec_stack):
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in analysis["dependency_graph"].get(node, []):
                    if neighbor not in visited:
                        if has_circular_ref(neighbor, visited, rec_stack):
                            return True
                    elif neighbor in rec_stack:
                        return True
                
                rec_stack.remove(node)
                return False
            
            visited = set()
            for feature_name in self.features:
                if feature_name not in visited:
                    if has_circular_ref(feature_name, visited, set()):
                        analysis["circular_references"].append(feature_name)
            
            # Find orphaned features (no dependencies and not depended upon)
            all_dependencies = set()
            for deps in analysis["dependency_graph"].values():
                all_dependencies.update(deps)
            
            for feature_name in self.features:
                if (not analysis["dependency_graph"].get(feature_name, []) and 
                    feature_name not in all_dependencies):
                    analysis["orphaned_features"].append(feature_name)
            
            # Calculate dependency depth
            def calculate_depth(node, memo):
                if node in memo:
                    return memo[node]
                
                dependencies = analysis["dependency_graph"].get(node, [])
                if not dependencies:
                    memo[node] = 0
                    return 0
                
                max_depth = max(calculate_depth(dep, memo) for dep in dependencies)
                memo[node] = max_depth + 1
                return memo[node]
            
            depth_memo = {}
            for feature_name in self.features:
                analysis["dependency_depth"][feature_name] = calculate_depth(feature_name, depth_memo)
            
            logger.info(f"Feature dependency analysis complete")
            
        except Exception as e:
            logger.error(f"Feature dependency analysis failed: {e}")
            analysis["error"] = str(e)
        
        return analysis
    
    def generate_manufacturing_report(self) -> str:
        """Generate manufacturing analysis report for all features"""
        try:
            report = "# Manufacturing Analysis Report\n\n"
            
            # Group features by manufacturing process
            process_groups = {}
            for feature_name, feature in self.features.items():
                process_hint = feature.manufacturing_notes.get("process_hint", "general")
                if process_hint not in process_groups:
                    process_groups[process_hint] = []
                process_groups[process_hint].append(feature_name)
            
            report += "## Process Groups\n"
            for process, features in process_groups.items():
                report += f"### {process.replace('_', ' ').title()}\n"
                for feature_name in features:
                    feature = self.features[feature_name]
                    report += f"- **{feature_name}** ({feature.feature_type.value})\n"
                    
                    # Add manufacturing-specific details
                    if feature.feature_type == FeatureType.HOLE:
                        diameter = feature.parameters.get("diameter", 0)
                        depth = feature.parameters.get("depth", 0)
                        aspect_ratio = feature.manufacturing_notes.get("aspect_ratio", 0)
                        report += f"  - Diameter: {diameter:.2f}mm, Depth: {depth:.2f}mm\n"
                        report += f"  - Aspect ratio: {aspect_ratio:.2f}\n"
                        
                        if aspect_ratio > 5:
                            report += "  - ⚠️ High aspect ratio - consider stepped drilling\n"
                    
                    elif feature.feature_type == FeatureType.FILLET:
                        radius = feature.parameters.get("radius", 0)
                        report += f"  - Radius: {radius:.2f}mm\n"
                        report += "  - Improves stress concentration\n"
                    
                    # Add warnings from manufacturing notes
                    warning = feature.manufacturing_notes.get("warning")
                    if warning:
                        report += f"  - ⚠️ {warning.replace('_', ' ').title()}\n"
                    
                    recommendation = feature.manufacturing_notes.get("recommendation")
                    if recommendation:
                        report += f"  - 💡 {recommendation.replace('_', ' ').title()}\n"
                
                report += "\n"
            
            # Add general recommendations
            report += "## General Recommendations\n"
            
            hole_features = [f for f in self.features.values() if f.feature_type == FeatureType.HOLE]
            if hole_features:
                high_aspect_holes = [f for f in hole_features if f.manufacturing_notes.get("aspect_ratio", 0) > 5]
                if high_aspect_holes:
                    report += f"- Consider stepped drilling for {len(high_aspect_holes)} high aspect ratio holes\n"
            
            fillet_features = [f for f in self.features.values() if f.feature_type == FeatureType.FILLET]
            if fillet_features:
                report += f"- {len(fillet_features)} fillet features will improve part durability\n"
            
            pattern_features = [f for f in self.features.values() if f.feature_type == FeatureType.PATTERN]
            if pattern_features:
                report += f"- {len(pattern_features)} pattern features enable batch processing efficiency\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate manufacturing report: {e}")
            return f"Error generating manufacturing report: {e}"
    
    def _get_dependencies_for_edges(self, edges: List[str]) -> List[str]:
        """Get feature dependencies for edge references"""
        # In a real implementation, this would parse edge references
        # and return the features that create those edges
        dependencies = []
        for edge in edges:
            # Simple parsing: assume format "FeatureName.Edge1"
            if "." in edge:
                feature_name = edge.split(".")[0]
                if feature_name in self.features:
                    dependencies.append(feature_name)
        return dependencies
    
    def export_feature_tree(self) -> Dict[str, Any]:
        """Export the complete feature tree structure"""
        return {
            "sketches": {name: {
                "plane": sketch.plane,
                "elements": len(sketch.elements),
                "constraints": len(sketch.constraints),
                "variables": sketch.variables
            } for name, sketch in self.sketches.items()},
            
            "features": {name: {
                "type": feature.feature_type.value,
                "parameters": feature.parameters,
                "dependencies": feature.dependencies,
                "sketch": feature.sketch_name,
                "manufacturing_notes": feature.manufacturing_notes
            } for name, feature in self.features.items()},
            
            "global_variables": self.global_variables,
            "feature_order": self.feature_tree
        }

# Utility functions for common CAD operations

def create_rectangular_sketch(cad_ops: AdvancedCADOperations, name: str, 
                             width: float, height: float, center: Tuple[float, float] = (0, 0)) -> bool:
    """Create a rectangular sketch with parametric dimensions"""
    try:
        sketch = cad_ops.create_parametric_sketch(name)
        
        x, y = center
        w, h = width / 2, height / 2
        
        # Add rectangle lines
        cad_ops.add_sketch_line(name, (x - w, y - h), (x + w, y - h), "bottom")
        cad_ops.add_sketch_line(name, (x + w, y - h), (x + w, y + h), "right")
        cad_ops.add_sketch_line(name, (x + w, y + h), (x - w, y + h), "top")
        cad_ops.add_sketch_line(name, (x - w, y + h), (x - w, y - h), "left")
        
        # Add constraints
        cad_ops.add_sketch_constraint(name, SketchConstraint("parallel", ["bottom", "top"]))
        cad_ops.add_sketch_constraint(name, SketchConstraint("parallel", ["left", "right"]))
        cad_ops.add_sketch_constraint(name, SketchConstraint("perpendicular", ["bottom", "right"]))
        cad_ops.add_sketch_constraint(name, SketchConstraint("equal", ["bottom", "top"]))
        cad_ops.add_sketch_constraint(name, SketchConstraint("equal", ["left", "right"]))
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create rectangular sketch: {e}")
        return False

def create_circular_sketch(cad_ops: AdvancedCADOperations, name: str, 
                          radius: float, center: Tuple[float, float] = (0, 0)) -> bool:
    """Create a circular sketch with parametric radius"""
    try:
        sketch = cad_ops.create_parametric_sketch(name)
        cad_ops.add_sketch_circle(name, center, radius, "main_circle")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create circular sketch: {e}")
        return False

def create_linear_pattern(cad_ops: AdvancedCADOperations, name: str, base_feature: str,
                         direction: Tuple[float, float, float], distance: float, count: int) -> bool:
    """Create a linear pattern of a feature"""
    parameters = {
        "direction": direction,
        "distance": distance,
        "count": count
    }
    return cad_ops.create_pattern_feature(name, base_feature, PatternType.LINEAR, parameters)

def create_circular_pattern(cad_ops: AdvancedCADOperations, name: str, base_feature: str,
                           axis: Tuple[float, float, float], angle: float, count: int) -> bool:
    """Create a circular pattern of a feature"""
    parameters = {
        "axis": axis,
        "angle": angle,
        "count": count
    }
    return cad_ops.create_pattern_feature(name, base_feature, PatternType.CIRCULAR, parameters)