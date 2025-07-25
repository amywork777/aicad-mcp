"""
Enhanced Spatial Reasoning Framework for FreeCAD
Provides physics-based spatial layout with collision detection, ergonomic analysis, and optimization.
"""

import math
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ObjectType(Enum):
    """Types of objects for spatial analysis"""
    MECHANICAL = "mechanical"
    ELECTRONIC = "electronic"
    STRUCTURAL = "structural"
    INTERFACE = "interface"
    SAFETY = "safety"

class ConstraintType(Enum):
    """Types of spatial constraints"""
    CLEARANCE = "clearance"
    ACCESSIBILITY = "accessibility"
    THERMAL = "thermal"
    ELECTROMAGNETIC = "electromagnetic"
    GRAVITY = "gravity"
    ERGONOMIC = "ergonomic"

@dataclass
class BoundingBox:
    """3D bounding box representation"""
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float
    
    @property
    def center(self) -> Tuple[float, float, float]:
        return (
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2,
            (self.min_z + self.max_z) / 2
        )
    
    @property
    def dimensions(self) -> Tuple[float, float, float]:
        return (
            self.max_x - self.min_x,
            self.max_y - self.min_y,
            self.max_z - self.min_z
        )
    
    def intersects(self, other: 'BoundingBox') -> bool:
        """Check if this bounding box intersects with another"""
        return (
            self.min_x <= other.max_x and self.max_x >= other.min_x and
            self.min_y <= other.max_y and self.max_y >= other.min_y and
            self.min_z <= other.max_z and self.max_z >= other.min_z
        )
    
    def distance_to(self, other: 'BoundingBox') -> float:
        """Calculate minimum distance between two bounding boxes"""
        dx = max(0, max(self.min_x - other.max_x, other.min_x - self.max_x))
        dy = max(0, max(self.min_y - other.max_y, other.min_y - self.max_y))
        dz = max(0, max(self.min_z - other.max_z, other.min_z - self.max_z))
        return math.sqrt(dx*dx + dy*dy + dz*dz)

@dataclass
class SpatialObject:
    """Object with spatial properties and constraints"""
    name: str
    obj_type: ObjectType
    position: Tuple[float, float, float]
    dimensions: Tuple[float, float, float]
    mass: float = 1.0
    fixed: bool = False
    clearance_requirements: Dict[str, float] = None
    thermal_properties: Dict[str, float] = None
    access_requirements: List[str] = None
    
    def __post_init__(self):
        if self.clearance_requirements is None:
            self.clearance_requirements = {}
        if self.thermal_properties is None:
            self.thermal_properties = {"heat_generation": 0.0, "max_temp": 85.0}
        if self.access_requirements is None:
            self.access_requirements = []
    
    @property
    def bounding_box(self) -> BoundingBox:
        """Get bounding box for this object"""
        x, y, z = self.position
        w, h, d = self.dimensions
        return BoundingBox(
            min_x=x - w/2, max_x=x + w/2,
            min_y=y - h/2, max_y=y + h/2,
            min_z=z - d/2, max_z=z + d/2
        )

@dataclass
class SpatialConstraint:
    """Constraint between spatial objects"""
    constraint_type: ConstraintType
    objects: List[str]
    parameters: Dict[str, Any]
    priority: int = 1  # 1=low, 5=critical
    
    def evaluate(self, objects: Dict[str, SpatialObject]) -> Dict[str, Any]:
        """Evaluate constraint and return violation details"""
        if self.constraint_type == ConstraintType.CLEARANCE:
            return self._evaluate_clearance(objects)
        elif self.constraint_type == ConstraintType.ACCESSIBILITY:
            return self._evaluate_accessibility(objects)
        elif self.constraint_type == ConstraintType.THERMAL:
            return self._evaluate_thermal(objects)
        elif self.constraint_type == ConstraintType.GRAVITY:
            return self._evaluate_gravity(objects)
        elif self.constraint_type == ConstraintType.ERGONOMIC:
            return self._evaluate_ergonomic(objects)
        else:
            return {"satisfied": True, "violation": 0.0, "details": "Unknown constraint type"}
    
    def _evaluate_clearance(self, objects: Dict[str, SpatialObject]) -> Dict[str, Any]:
        """Evaluate clearance constraint"""
        if len(self.objects) < 2:
            return {"satisfied": True, "violation": 0.0, "details": "Insufficient objects"}
        
        min_distance = self.parameters.get("min_distance", 5.0)
        obj1, obj2 = objects[self.objects[0]], objects[self.objects[1]]
        
        actual_distance = obj1.bounding_box.distance_to(obj2.bounding_box)
        violation = max(0, min_distance - actual_distance)
        
        return {
            "satisfied": violation == 0,
            "violation": violation,
            "actual_distance": actual_distance,
            "required_distance": min_distance,
            "details": f"Distance: {actual_distance:.2f}mm, Required: {min_distance:.2f}mm"
        }
    
    def _evaluate_accessibility(self, objects: Dict[str, SpatialObject]) -> Dict[str, Any]:
        """Evaluate accessibility constraint"""
        target_obj = objects[self.objects[0]]
        access_direction = self.parameters.get("direction", "top")
        access_distance = self.parameters.get("distance", 50.0)
        
        # Simple accessibility check - ensure space in access direction
        x, y, z = target_obj.position
        w, h, d = target_obj.dimensions
        
        if access_direction == "top":
            access_zone = BoundingBox(x-w/2, y-h/2, z+d/2, x+w/2, y+h/2, z+d/2+access_distance)
        elif access_direction == "front":
            access_zone = BoundingBox(x-w/2, y+h/2, z-d/2, x+w/2, y+h/2+access_distance, z+d/2)
        else:  # Default to top
            access_zone = BoundingBox(x-w/2, y-h/2, z+d/2, x+w/2, y+h/2, z+d/2+access_distance)
        
        # Check for obstructions
        obstructions = []
        for name, obj in objects.items():
            if name != self.objects[0] and obj.bounding_box.intersects(access_zone):
                obstructions.append(name)
        
        violation = len(obstructions)
        return {
            "satisfied": violation == 0,
            "violation": violation,
            "obstructions": obstructions,
            "access_direction": access_direction,
            "details": f"Access {access_direction}: {len(obstructions)} obstructions"
        }
    
    def _evaluate_thermal(self, objects: Dict[str, SpatialObject]) -> Dict[str, Any]:
        """Evaluate thermal constraint"""
        heat_source = objects[self.objects[0]]
        sensitive_obj = objects[self.objects[1]] if len(self.objects) > 1 else None
        
        max_temp_rise = self.parameters.get("max_temp_rise", 20.0)
        heat_gen = heat_source.thermal_properties.get("heat_generation", 0.0)
        
        if sensitive_obj:
            distance = heat_source.bounding_box.distance_to(sensitive_obj.bounding_box)
            # Simple thermal model: temp rise inversely proportional to distance squared
            temp_rise = heat_gen / max(1.0, distance ** 2) * 100
            violation = max(0, temp_rise - max_temp_rise)
            
            return {
                "satisfied": violation == 0,
                "violation": violation,
                "predicted_temp_rise": temp_rise,
                "max_allowed": max_temp_rise,
                "distance": distance,
                "details": f"Predicted temp rise: {temp_rise:.1f}°C, Max: {max_temp_rise:.1f}°C"
            }
        
        return {"satisfied": True, "violation": 0.0, "details": "No sensitive object specified"}
    
    def _evaluate_gravity(self, objects: Dict[str, SpatialObject]) -> Dict[str, Any]:
        """Evaluate gravity/stability constraint"""
        obj = objects[self.objects[0]]
        
        # Check if object is supported
        support_required = self.parameters.get("support_required", True)
        min_support_area = self.parameters.get("min_support_area", 0.1)
        
        if not support_required:
            return {"satisfied": True, "violation": 0.0, "details": "No support required"}
        
        # Simple check: object center of mass should be within support base
        x, y, z = obj.position
        w, h, d = obj.dimensions
        
        # Assume support comes from below (z-direction)
        support_area = w * d
        stability_margin = min(w, d) / 4  # 25% margin
        
        violation = max(0, min_support_area - support_area)
        
        return {
            "satisfied": violation == 0,
            "violation": violation,
            "support_area": support_area,
            "required_area": min_support_area,
            "stability_margin": stability_margin,
            "details": f"Support area: {support_area:.2f}mm², Required: {min_support_area:.2f}mm²"
        }
    
    def _evaluate_ergonomic(self, objects: Dict[str, SpatialObject]) -> Dict[str, Any]:
        """Evaluate ergonomic constraint"""
        obj = objects[self.objects[0]]
        x, y, z = obj.position
        
        # Ergonomic zones (heights in mm from floor)
        optimal_height = self.parameters.get("optimal_height", (700, 1200))
        max_reach = self.parameters.get("max_reach", 600)
        
        height_violation = 0
        if z < optimal_height[0]:
            height_violation = optimal_height[0] - z
        elif z > optimal_height[1]:
            height_violation = z - optimal_height[1]
        
        reach_distance = math.sqrt(x*x + y*y)
        reach_violation = max(0, reach_distance - max_reach)
        
        total_violation = height_violation + reach_violation
        
        return {
            "satisfied": total_violation == 0,
            "violation": total_violation,
            "height_violation": height_violation,
            "reach_violation": reach_violation,
            "current_height": z,
            "optimal_range": optimal_height,
            "reach_distance": reach_distance,
            "details": f"Height: {z:.0f}mm (optimal: {optimal_height[0]}-{optimal_height[1]}mm), Reach: {reach_distance:.0f}mm"
        }

class EnhancedSpatialFramework:
    """Enhanced spatial reasoning framework with physics-based constraints"""
    
    def __init__(self):
        self.objects: Dict[str, SpatialObject] = {}
        self.constraints: List[SpatialConstraint] = []
        self.layout_bounds = BoundingBox(-1000, -1000, 0, 1000, 1000, 2000)  # Default workspace
        
    def add_object(self, obj: SpatialObject) -> bool:
        """Add spatial object to the framework"""
        try:
            # Validate object fits within layout bounds
            obj_bbox = obj.bounding_box
            if not self._bbox_within_bounds(obj_bbox, self.layout_bounds):
                logger.warning(f"Object {obj.name} extends beyond layout bounds")
            
            self.objects[obj.name] = obj
            logger.info(f"Added spatial object: {obj.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add spatial object {obj.name}: {e}")
            return False
    
    def add_constraint(self, constraint: SpatialConstraint) -> bool:
        """Add spatial constraint to the framework"""
        try:
            # Validate constraint objects exist
            for obj_name in constraint.objects:
                if obj_name not in self.objects:
                    logger.error(f"Constraint references unknown object: {obj_name}")
                    return False
            
            self.constraints.append(constraint)
            logger.info(f"Added constraint: {constraint.constraint_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add constraint: {e}")
            return False
    
    def evaluate_layout(self) -> Dict[str, Any]:
        """Evaluate current spatial layout against all constraints"""
        results = {
            "overall_score": 0.0,
            "total_violations": 0,
            "constraint_results": [],
            "object_status": {},
            "recommendations": []
        }
        
        try:
            total_weight = 0
            total_score = 0
            
            # Evaluate each constraint
            for constraint in self.constraints:
                result = constraint.evaluate(self.objects)
                result["constraint_type"] = constraint.constraint_type.value
                result["priority"] = constraint.priority
                result["objects"] = constraint.objects
                
                # Weight score by priority
                weight = constraint.priority
                score = 100 if result["satisfied"] else max(0, 100 - result["violation"] * 10)
                
                total_weight += weight
                total_score += score * weight
                
                if not result["satisfied"]:
                    results["total_violations"] += 1
                
                results["constraint_results"].append(result)
            
            # Calculate overall score
            results["overall_score"] = total_score / max(1, total_weight)
            
            # Generate object status
            for name, obj in self.objects.items():
                obj_constraints = [c for c in self.constraints if name in c.objects]
                obj_violations = sum(1 for c in obj_constraints if not c.evaluate(self.objects)["satisfied"])
                
                results["object_status"][name] = {
                    "position": obj.position,
                    "dimensions": obj.dimensions,
                    "constraints": len(obj_constraints),
                    "violations": obj_violations,
                    "status": "OK" if obj_violations == 0 else "VIOLATION"
                }
            
            # Generate recommendations
            results["recommendations"] = self._generate_recommendations(results)
            
            logger.info(f"Layout evaluation complete: {results['overall_score']:.1f}/100, {results['total_violations']} violations")
            
        except Exception as e:
            logger.error(f"Layout evaluation failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def optimize_layout(self, max_iterations: int = 100) -> Dict[str, Any]:
        """Optimize spatial layout using constraint-based approach"""
        optimization_results = {
            "initial_score": 0.0,
            "final_score": 0.0,
            "iterations": 0,
            "improvements": [],
            "final_positions": {}
        }
        
        try:
            # Get initial evaluation
            initial_eval = self.evaluate_layout()
            optimization_results["initial_score"] = initial_eval["overall_score"]
            
            best_score = initial_eval["overall_score"]
            best_positions = {name: obj.position for name, obj in self.objects.items()}
            
            for iteration in range(max_iterations):
                # Try to improve layout by adjusting object positions
                improved = False
                
                for obj_name, obj in self.objects.items():
                    if obj.fixed:
                        continue
                    
                    # Try small random adjustments
                    original_pos = obj.position
                    
                    for _ in range(10):  # Try 10 random adjustments per object
                        # Generate small random displacement
                        dx = (math.random() - 0.5) * 20  # ±10mm
                        dy = (math.random() - 0.5) * 20
                        dz = (math.random() - 0.5) * 10  # Smaller Z adjustment
                        
                        new_pos = (
                            original_pos[0] + dx,
                            original_pos[1] + dy,
                            original_pos[2] + dz
                        )
                        
                        # Check if new position is within bounds
                        obj.position = new_pos
                        if not self._bbox_within_bounds(obj.bounding_box, self.layout_bounds):
                            obj.position = original_pos
                            continue
                        
                        # Evaluate new layout
                        eval_result = self.evaluate_layout()
                        
                        if eval_result["overall_score"] > best_score:
                            best_score = eval_result["overall_score"]
                            best_positions[obj_name] = new_pos
                            improved = True
                            
                            optimization_results["improvements"].append({
                                "iteration": iteration,
                                "object": obj_name,
                                "old_position": original_pos,
                                "new_position": new_pos,
                                "score_improvement": eval_result["overall_score"] - optimization_results["initial_score"]
                            })
                            break
                        else:
                            # Revert position
                            obj.position = original_pos
                
                if not improved:
                    break
                
                optimization_results["iterations"] = iteration + 1
            
            # Apply best positions
            for obj_name, pos in best_positions.items():
                self.objects[obj_name].position = pos
            
            optimization_results["final_score"] = best_score
            optimization_results["final_positions"] = best_positions
            
            logger.info(f"Layout optimization complete: {optimization_results['initial_score']:.1f} → {optimization_results['final_score']:.1f} in {optimization_results['iterations']} iterations")
            
        except Exception as e:
            logger.error(f"Layout optimization failed: {e}")
            optimization_results["error"] = str(e)
        
        return optimization_results
    
    def detect_collisions(self) -> List[Dict[str, Any]]:
        """Detect collisions between objects"""
        collisions = []
        
        try:
            object_names = list(self.objects.keys())
            
            for i in range(len(object_names)):
                for j in range(i + 1, len(object_names)):
                    obj1_name = object_names[i]
                    obj2_name = object_names[j]
                    obj1 = self.objects[obj1_name]
                    obj2 = self.objects[obj2_name]
                    
                    if obj1.bounding_box.intersects(obj2.bounding_box):
                        # Calculate overlap volume
                        bbox1, bbox2 = obj1.bounding_box, obj2.bounding_box
                        
                        overlap_x = min(bbox1.max_x, bbox2.max_x) - max(bbox1.min_x, bbox2.min_x)
                        overlap_y = min(bbox1.max_y, bbox2.max_y) - max(bbox1.min_y, bbox2.min_y)
                        overlap_z = min(bbox1.max_z, bbox2.max_z) - max(bbox1.min_z, bbox2.min_z)
                        
                        overlap_volume = max(0, overlap_x) * max(0, overlap_y) * max(0, overlap_z)
                        
                        collisions.append({
                            "object1": obj1_name,
                            "object2": obj2_name,
                            "overlap_volume": overlap_volume,
                            "severity": "critical" if overlap_volume > 1000 else "moderate",
                            "resolution": self._suggest_collision_resolution(obj1, obj2)
                        })
            
            logger.info(f"Collision detection complete: {len(collisions)} collisions found")
            
        except Exception as e:
            logger.error(f"Collision detection failed: {e}")
        
        return collisions
    
    def _bbox_within_bounds(self, bbox: BoundingBox, bounds: BoundingBox) -> bool:
        """Check if bounding box is within specified bounds"""
        return (
            bbox.min_x >= bounds.min_x and bbox.max_x <= bounds.max_x and
            bbox.min_y >= bounds.min_y and bbox.max_y <= bounds.max_y and
            bbox.min_z >= bounds.min_z and bbox.max_z <= bounds.max_z
        )
    
    def _generate_recommendations(self, evaluation: Dict[str, Any]) -> List[str]:
        """Generate layout improvement recommendations"""
        recommendations = []
        
        try:
            # Analyze constraint violations
            for result in evaluation["constraint_results"]:
                if not result["satisfied"]:
                    if result["constraint_type"] == "clearance":
                        recommendations.append(
                            f"Increase distance between {' and '.join(result['objects'])} "
                            f"(current: {result.get('actual_distance', 0):.1f}mm, "
                            f"required: {result.get('required_distance', 0):.1f}mm)"
                        )
                    elif result["constraint_type"] == "accessibility":
                        recommendations.append(
                            f"Clear access path for {result['objects'][0]} "
                            f"({result['access_direction']} direction blocked by {', '.join(result.get('obstructions', []))})"
                        )
                    elif result["constraint_type"] == "thermal":
                        recommendations.append(
                            f"Increase thermal separation between {' and '.join(result['objects'])} "
                            f"(predicted temp rise: {result.get('predicted_temp_rise', 0):.1f}°C)"
                        )
                    elif result["constraint_type"] == "ergonomic":
                        recommendations.append(
                            f"Adjust {result['objects'][0]} to ergonomic zone "
                            f"(current height: {result.get('current_height', 0):.0f}mm, "
                            f"optimal: {result.get('optimal_range', (0, 0))[0]}-{result.get('optimal_range', (0, 0))[1]}mm)"
                        )
            
            # General recommendations based on overall score
            score = evaluation["overall_score"]
            if score < 50:
                recommendations.append("Consider major layout redesign - multiple critical violations detected")
            elif score < 70:
                recommendations.append("Layout needs improvement - focus on constraint violations")
            elif score < 90:
                recommendations.append("Layout is acceptable but could be optimized further")
            
            # Collision-specific recommendations
            collisions = self.detect_collisions()
            if collisions:
                recommendations.append(f"Resolve {len(collisions)} object collisions")
                
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            recommendations.append("Error generating recommendations - check logs")
        
        return recommendations
    
    def _suggest_collision_resolution(self, obj1: SpatialObject, obj2: SpatialObject) -> str:
        """Suggest resolution for object collision"""
        if obj1.fixed and obj2.fixed:
            return "Both objects fixed - design change required"
        elif obj1.fixed:
            return f"Move {obj2.name} away from fixed {obj1.name}"
        elif obj2.fixed:
            return f"Move {obj1.name} away from fixed {obj2.name}"
        else:
            # Move the smaller/lighter object
            if obj1.mass < obj2.mass:
                return f"Move smaller object {obj1.name}"
            else:
                return f"Move smaller object {obj2.name}"
    
    def generate_layout_report(self) -> str:
        """Generate comprehensive spatial layout report"""
        try:
            evaluation = self.evaluate_layout()
            collisions = self.detect_collisions()
            
            report = f"""
# Spatial Layout Analysis Report

## Overview
- **Overall Score**: {evaluation['overall_score']:.1f}/100
- **Total Objects**: {len(self.objects)}
- **Total Constraints**: {len(self.constraints)}
- **Violations**: {evaluation['total_violations']}
- **Collisions**: {len(collisions)}

## Object Status
"""
            
            for name, status in evaluation["object_status"].items():
                report += f"- **{name}**: {status['status']} ({status['violations']} violations)\n"
                report += f"  - Position: ({status['position'][0]:.1f}, {status['position'][1]:.1f}, {status['position'][2]:.1f})\n"
                report += f"  - Dimensions: {status['dimensions'][0]:.1f} × {status['dimensions'][1]:.1f} × {status['dimensions'][2]:.1f}\n"
            
            report += "\n## Constraint Analysis\n"
            for result in evaluation["constraint_results"]:
                status = "✓ PASS" if result["satisfied"] else "✗ FAIL"
                report += f"- **{result['constraint_type'].upper()}** {status}: {result['details']}\n"
            
            if collisions:
                report += "\n## Collisions Detected\n"
                for collision in collisions:
                    report += f"- **{collision['object1']} ↔ {collision['object2']}**: "
                    report += f"Overlap {collision['overlap_volume']:.1f}mm³ ({collision['severity']})\n"
                    report += f"  - Resolution: {collision['resolution']}\n"
            
            report += "\n## Recommendations\n"
            for rec in evaluation["recommendations"]:
                report += f"- {rec}\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate layout report: {e}")
            return f"Error generating report: {e}"

# Utility functions for creating common spatial objects and constraints

def create_mechanical_component(name: str, position: Tuple[float, float, float], 
                              dimensions: Tuple[float, float, float], 
                              mass: float = 1.0, fixed: bool = False) -> SpatialObject:
    """Create a mechanical component with default properties"""
    return SpatialObject(
        name=name,
        obj_type=ObjectType.MECHANICAL,
        position=position,
        dimensions=dimensions,
        mass=mass,
        fixed=fixed,
        clearance_requirements={"default": 5.0, "maintenance": 25.0},
        thermal_properties={"heat_generation": 0.1, "max_temp": 85.0},
        access_requirements=["maintenance", "inspection"]
    )

def create_electronic_component(name: str, position: Tuple[float, float, float],
                               dimensions: Tuple[float, float, float],
                               heat_generation: float = 2.0) -> SpatialObject:
    """Create an electronic component with thermal properties"""
    return SpatialObject(
        name=name,
        obj_type=ObjectType.ELECTRONIC,
        position=position,
        dimensions=dimensions,
        mass=0.1,
        clearance_requirements={"default": 3.0, "thermal": 10.0},
        thermal_properties={"heat_generation": heat_generation, "max_temp": 70.0},
        access_requirements=["service", "replacement"]
    )

def create_clearance_constraint(obj1: str, obj2: str, min_distance: float, 
                               priority: int = 3) -> SpatialConstraint:
    """Create a clearance constraint between two objects"""
    return SpatialConstraint(
        constraint_type=ConstraintType.CLEARANCE,
        objects=[obj1, obj2],
        parameters={"min_distance": min_distance},
        priority=priority
    )

def create_accessibility_constraint(obj: str, direction: str = "top", 
                                   distance: float = 50.0, priority: int = 4) -> SpatialConstraint:
    """Create an accessibility constraint for an object"""
    return SpatialConstraint(
        constraint_type=ConstraintType.ACCESSIBILITY,
        objects=[obj],
        parameters={"direction": direction, "distance": distance},
        priority=priority
    )

def create_ergonomic_constraint(obj: str, optimal_height: Tuple[float, float] = (700, 1200),
                               max_reach: float = 600, priority: int = 3) -> SpatialConstraint:
    """Create an ergonomic constraint for human interaction"""
    return SpatialConstraint(
        constraint_type=ConstraintType.ERGONOMIC,
        objects=[obj],
        parameters={"optimal_height": optimal_height, "max_reach": max_reach},
        priority=priority
    )