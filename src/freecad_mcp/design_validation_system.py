"""
Design Validation System for FreeCAD
Comprehensive validation framework for geometry, manufacturing, structural, assembly, and cost analysis.
"""

import math
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationCategory(Enum):
    """Categories of validation checks"""
    GEOMETRY = "geometry"
    MANUFACTURING = "manufacturing"
    STRUCTURAL = "structural"
    ASSEMBLY = "assembly"
    COST = "cost"
    COMPLIANCE = "compliance"
    SUSTAINABILITY = "sustainability"

@dataclass
class ValidationIssue:
    """Individual validation issue"""
    category: ValidationCategory
    severity: ValidationSeverity
    title: str
    description: str
    affected_objects: List[str]
    location: Optional[Tuple[float, float, float]] = None
    recommendation: Optional[str] = None
    cost_impact: Optional[float] = None
    time_impact: Optional[float] = None
    compliance_standard: Optional[str] = None
    
@dataclass
class ValidationRule:
    """Validation rule definition"""
    name: str
    category: ValidationCategory
    severity: ValidationSeverity
    description: str
    parameters: Dict[str, Any]
    enabled: bool = True

@dataclass
class ValidationResult:
    """Complete validation result"""
    timestamp: datetime
    overall_score: float
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues_by_category: Dict[str, int]
    issues: List[ValidationIssue]
    recommendations: List[str]
    estimated_cost_impact: float
    estimated_time_impact: float

class GeometryValidator:
    """Validates geometric properties and integrity"""
    
    def __init__(self):
        self.min_wall_thickness = 0.8  # mm
        self.min_feature_size = 0.5    # mm
        self.max_aspect_ratio = 20.0
        self.min_angle = 0.5           # degrees
        
    def validate_wall_thickness(self, objects: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate minimum wall thickness"""
        issues = []
        
        try:
            for obj_name, obj_data in objects.items():
                # Mock wall thickness analysis
                faces = obj_data.get("faces", [])
                
                for face_idx, face in enumerate(faces):
                    thickness = face.get("thickness", 0)
                    
                    if thickness > 0 and thickness < self.min_wall_thickness:
                        severity = ValidationSeverity.ERROR if thickness < 0.3 else ValidationSeverity.WARNING
                        
                        issues.append(ValidationIssue(
                            category=ValidationCategory.GEOMETRY,
                            severity=severity,
                            title="Insufficient Wall Thickness",
                            description=f"Wall thickness {thickness:.2f}mm is below minimum {self.min_wall_thickness:.2f}mm",
                            affected_objects=[obj_name],
                            location=face.get("center"),
                            recommendation=f"Increase wall thickness to at least {self.min_wall_thickness:.2f}mm",
                            cost_impact=0.1,  # Relative cost increase
                            time_impact=2.0   # Hours to fix
                        ))
                        
        except Exception as e:
            logger.error(f"Wall thickness validation failed: {e}")
            
        return issues
    
    def validate_feature_sizes(self, objects: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate minimum feature sizes"""
        issues = []
        
        try:
            for obj_name, obj_data in objects.items():
                features = obj_data.get("features", [])
                
                for feature in features:
                    feature_type = feature.get("type")
                    size = feature.get("size", 0)
                    
                    if size < self.min_feature_size:
                        severity = ValidationSeverity.ERROR if size < 0.2 else ValidationSeverity.WARNING
                        
                        issues.append(ValidationIssue(
                            category=ValidationCategory.GEOMETRY,
                            severity=severity,
                            title="Feature Too Small",
                            description=f"{feature_type} feature size {size:.2f}mm is below minimum {self.min_feature_size:.2f}mm",
                            affected_objects=[obj_name],
                            location=feature.get("location"),
                            recommendation=f"Increase {feature_type} size to at least {self.min_feature_size:.2f}mm",
                            cost_impact=0.05,
                            time_impact=1.0
                        ))
                        
        except Exception as e:
            logger.error(f"Feature size validation failed: {e}")
            
        return issues
    
    def validate_hole_geometry(self, objects: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate hole geometry and aspect ratios"""
        issues = []
        
        try:
            for obj_name, obj_data in objects.items():
                holes = obj_data.get("holes", [])
                
                for hole in holes:
                    diameter = hole.get("diameter", 0)
                    depth = hole.get("depth", 0)
                    
                    if diameter > 0 and depth > 0:
                        aspect_ratio = depth / diameter
                        
                        if aspect_ratio > self.max_aspect_ratio:
                            issues.append(ValidationIssue(
                                category=ValidationCategory.GEOMETRY,
                                severity=ValidationSeverity.WARNING,
                                title="High Aspect Ratio Hole",
                                description=f"Hole aspect ratio {aspect_ratio:.1f} exceeds recommended maximum {self.max_aspect_ratio}",
                                affected_objects=[obj_name],
                                location=hole.get("position"),
                                recommendation="Consider stepped drilling or reduce depth",
                                cost_impact=0.15,
                                time_impact=1.5
                            ))
                        
                        # Check minimum hole diameter
                        if diameter < 1.0:
                            issues.append(ValidationIssue(
                                category=ValidationCategory.GEOMETRY,
                                severity=ValidationSeverity.WARNING,
                                title="Small Hole Diameter",
                                description=f"Hole diameter {diameter:.2f}mm may be difficult to manufacture accurately",
                                affected_objects=[obj_name],
                                location=hole.get("position"),
                                recommendation="Consider increasing diameter or using specialized tooling",
                                cost_impact=0.08,
                                time_impact=0.5
                            ))
                            
        except Exception as e:
            logger.error(f"Hole geometry validation failed: {e}")
            
        return issues

class ManufacturingValidator:
    """Validates manufacturability for different processes"""
    
    def __init__(self):
        self.processes = {
            "fdm_3d_printing": {
                "min_wall_thickness": 1.2,
                "min_feature_size": 0.8,
                "max_overhang_angle": 45,
                "min_clearance": 0.4
            },
            "cnc_machining": {
                "min_wall_thickness": 0.5,
                "min_feature_size": 0.1,
                "min_corner_radius": 0.1,
                "max_aspect_ratio": 10
            },
            "injection_molding": {
                "min_wall_thickness": 0.8,
                "max_wall_thickness": 4.0,
                "min_draft_angle": 0.5,
                "min_corner_radius": 0.25
            }
        }
    
    def validate_for_process(self, objects: Dict[str, Any], process: str) -> List[ValidationIssue]:
        """Validate design for specific manufacturing process"""
        issues = []
        
        if process not in self.processes:
            logger.warning(f"Unknown manufacturing process: {process}")
            return issues
        
        process_params = self.processes[process]
        
        try:
            if process == "fdm_3d_printing":
                issues.extend(self._validate_fdm_3d_printing(objects, process_params))
            elif process == "cnc_machining":
                issues.extend(self._validate_cnc_machining(objects, process_params))
            elif process == "injection_molding":
                issues.extend(self._validate_injection_molding(objects, process_params))
                
        except Exception as e:
            logger.error(f"Manufacturing validation for {process} failed: {e}")
            
        return issues
    
    def _validate_fdm_3d_printing(self, objects: Dict[str, Any], params: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate for FDM 3D printing"""
        issues = []
        
        for obj_name, obj_data in objects.items():
            # Check overhangs
            overhangs = obj_data.get("overhangs", [])
            for overhang in overhangs:
                angle = overhang.get("angle", 90)
                if angle > params["max_overhang_angle"]:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.MANUFACTURING,
                        severity=ValidationSeverity.WARNING,
                        title="Unsupported Overhang",
                        description=f"Overhang angle {angle}° exceeds maximum {params['max_overhang_angle']}° for FDM printing",
                        affected_objects=[obj_name],
                        location=overhang.get("location"),
                        recommendation="Add support structures or redesign geometry",
                        cost_impact=0.2,
                        time_impact=3.0
                    ))
            
            # Check bridging
            bridges = obj_data.get("bridges", [])
            for bridge in bridges:
                length = bridge.get("length", 0)
                if length > 20:  # mm
                    issues.append(ValidationIssue(
                        category=ValidationCategory.MANUFACTURING,
                        severity=ValidationSeverity.WARNING,
                        title="Long Bridge",
                        description=f"Bridge length {length:.1f}mm may cause sagging in FDM printing",
                        affected_objects=[obj_name],
                        location=bridge.get("location"),
                        recommendation="Add intermediate supports or reduce bridge length",
                        cost_impact=0.1,
                        time_impact=2.0
                    ))
        
        return issues
    
    def _validate_cnc_machining(self, objects: Dict[str, Any], params: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate for CNC machining"""
        issues = []
        
        for obj_name, obj_data in objects.items():
            # Check tool access
            pockets = obj_data.get("pockets", [])
            for pocket in pockets:
                depth = pocket.get("depth", 0)
                width = pocket.get("width", 0)
                
                if width > 0 and depth / width > params["max_aspect_ratio"]:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.MANUFACTURING,
                        severity=ValidationSeverity.ERROR,
                        title="Deep Narrow Pocket",
                        description=f"Pocket aspect ratio {depth/width:.1f} exceeds CNC tooling limits",
                        affected_objects=[obj_name],
                        location=pocket.get("location"),
                        recommendation="Increase pocket width or reduce depth",
                        cost_impact=0.3,
                        time_impact=4.0
                    ))
            
            # Check internal corners
            corners = obj_data.get("internal_corners", [])
            for corner in corners:
                radius = corner.get("radius", 0)
                if radius < params["min_corner_radius"]:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.MANUFACTURING,
                        severity=ValidationSeverity.WARNING,
                        title="Sharp Internal Corner",
                        description=f"Internal corner radius {radius:.2f}mm is below minimum {params['min_corner_radius']:.2f}mm for CNC",
                        affected_objects=[obj_name],
                        location=corner.get("location"),
                        recommendation=f"Add fillet with radius ≥ {params['min_corner_radius']:.2f}mm",
                        cost_impact=0.1,
                        time_impact=1.0
                    ))
        
        return issues
    
    def _validate_injection_molding(self, objects: Dict[str, Any], params: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate for injection molding"""
        issues = []
        
        for obj_name, obj_data in objects.items():
            # Check draft angles
            surfaces = obj_data.get("vertical_surfaces", [])
            for surface in surfaces:
                draft_angle = surface.get("draft_angle", 0)
                if draft_angle < params["min_draft_angle"]:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.MANUFACTURING,
                        severity=ValidationSeverity.ERROR,
                        title="Insufficient Draft Angle",
                        description=f"Draft angle {draft_angle:.2f}° is below minimum {params['min_draft_angle']:.2f}° for injection molding",
                        affected_objects=[obj_name],
                        location=surface.get("location"),
                        recommendation=f"Add draft angle ≥ {params['min_draft_angle']:.2f}°",
                        cost_impact=0.25,
                        time_impact=3.0
                    ))
            
            # Check wall thickness variation
            wall_thickness_variation = obj_data.get("wall_thickness_variation", 0)
            if wall_thickness_variation > 0.5:  # 50% variation
                issues.append(ValidationIssue(
                    category=ValidationCategory.MANUFACTURING,
                    severity=ValidationSeverity.WARNING,
                    title="High Wall Thickness Variation",
                    description=f"Wall thickness variation {wall_thickness_variation*100:.0f}% may cause warping",
                    affected_objects=[obj_name],
                    recommendation="Aim for uniform wall thickness",
                    cost_impact=0.15,
                    time_impact=2.5
                ))
        
        return issues

class StructuralValidator:
    """Validates structural integrity and mechanical properties"""
    
    def __init__(self):
        self.safety_factor = 2.0
        self.max_stress = 200e6  # Pa (200 MPa for typical steel)
        self.max_deflection = 0.001  # 1mm per meter
        
    def validate_stress_concentrations(self, objects: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate stress concentration factors"""
        issues = []
        
        try:
            for obj_name, obj_data in objects.items():
                stress_concentrations = obj_data.get("stress_concentrations", [])
                
                for concentration in stress_concentrations:
                    factor = concentration.get("concentration_factor", 1.0)
                    location = concentration.get("location")
                    
                    if factor > 3.0:
                        severity = ValidationSeverity.ERROR if factor > 5.0 else ValidationSeverity.WARNING
                        
                        issues.append(ValidationIssue(
                            category=ValidationCategory.STRUCTURAL,
                            severity=severity,
                            title="High Stress Concentration",
                            description=f"Stress concentration factor {factor:.1f} at critical location",
                            affected_objects=[obj_name],
                            location=location,
                            recommendation="Add fillets or chamfers to reduce stress concentration",
                            cost_impact=0.1,
                            time_impact=2.0
                        ))
                        
        except Exception as e:
            logger.error(f"Stress concentration validation failed: {e}")
            
        return issues
    
    def validate_load_paths(self, objects: Dict[str, Any], loads: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate load transfer paths"""
        issues = []
        
        try:
            for load_name, load_data in loads.items():
                magnitude = load_data.get("magnitude", 0)
                application_point = load_data.get("point")
                
                # Check if load path exists to supports
                supports = load_data.get("supports", [])
                
                if not supports:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.STRUCTURAL,
                        severity=ValidationSeverity.CRITICAL,
                        title="No Load Path to Support",
                        description=f"Load {load_name} ({magnitude:.1f}N) has no clear path to supports",
                        affected_objects=load_data.get("affected_objects", []),
                        location=application_point,
                        recommendation="Ensure continuous load path to structural supports",
                        cost_impact=0.5,
                        time_impact=8.0
                    ))
                
                # Check load magnitude vs cross-sectional area
                cross_section_area = load_data.get("cross_section_area", 1)
                stress = magnitude / cross_section_area
                
                if stress > self.max_stress / self.safety_factor:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.STRUCTURAL,
                        severity=ValidationSeverity.ERROR,
                        title="Excessive Stress",
                        description=f"Calculated stress {stress/1e6:.1f}MPa exceeds allowable {self.max_stress/1e6/self.safety_factor:.1f}MPa",
                        affected_objects=load_data.get("affected_objects", []),
                        location=application_point,
                        recommendation="Increase cross-sectional area or reduce load",
                        cost_impact=0.3,
                        time_impact=5.0
                    ))
                    
        except Exception as e:
            logger.error(f"Load path validation failed: {e}")
            
        return issues

class AssemblyValidator:
    """Validates assembly constraints and fit tolerances"""
    
    def __init__(self):
        self.tolerance_grades = {
            "H7": 0.025,  # mm for ~25mm diameter
            "H8": 0.039,
            "H9": 0.062,
            "g6": -0.013,
            "f7": -0.025
        }
        
    def validate_fit_tolerances(self, assemblies: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate fit tolerances between mating parts"""
        issues = []
        
        try:
            for assembly_name, assembly_data in assemblies.items():
                fits = assembly_data.get("fits", [])
                
                for fit in fits:
                    fit_type = fit.get("type")  # clearance, transition, interference
                    shaft_tolerance = fit.get("shaft_tolerance")
                    hole_tolerance = fit.get("hole_tolerance")
                    nominal_size = fit.get("nominal_size", 25)  # mm
                    
                    # Calculate actual clearance/interference
                    shaft_dev = self.tolerance_grades.get(shaft_tolerance, 0)
                    hole_dev = self.tolerance_grades.get(hole_tolerance, 0)
                    
                    clearance = hole_dev - shaft_dev
                    
                    if fit_type == "clearance" and clearance <= 0:
                        issues.append(ValidationIssue(
                            category=ValidationCategory.ASSEMBLY,
                            severity=ValidationSeverity.ERROR,
                            title="Insufficient Clearance",
                            description=f"Clearance fit has {clearance*1000:.1f}μm clearance (should be positive)",
                            affected_objects=[fit.get("shaft_part"), fit.get("hole_part")],
                            recommendation="Adjust tolerance grades to ensure positive clearance",
                            cost_impact=0.2,
                            time_impact=3.0
                        ))
                    
                    elif fit_type == "interference" and clearance >= 0:
                        issues.append(ValidationIssue(
                            category=ValidationCategory.ASSEMBLY,
                            severity=ValidationSeverity.ERROR,
                            title="Insufficient Interference",
                            description=f"Interference fit has {clearance*1000:.1f}μm clearance (should be negative)",
                            affected_objects=[fit.get("shaft_part"), fit.get("hole_part")],
                            recommendation="Adjust tolerance grades to ensure interference",
                            cost_impact=0.2,
                            time_impact=3.0
                        ))
                        
        except Exception as e:
            logger.error(f"Fit tolerance validation failed: {e}")
            
        return issues
    
    def validate_assembly_sequence(self, assemblies: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate assembly sequence and accessibility"""
        issues = []
        
        try:
            for assembly_name, assembly_data in assemblies.items():
                sequence = assembly_data.get("assembly_sequence", [])
                
                for step_idx, step in enumerate(sequence):
                    part_name = step.get("part")
                    tool_access = step.get("tool_access", True)
                    clearance_available = step.get("clearance", True)
                    
                    if not tool_access:
                        issues.append(ValidationIssue(
                            category=ValidationCategory.ASSEMBLY,
                            severity=ValidationSeverity.WARNING,
                            title="Limited Tool Access",
                            description=f"Step {step_idx + 1}: Limited tool access for {part_name}",
                            affected_objects=[part_name],
                            recommendation="Ensure adequate tool access or modify assembly sequence",
                            cost_impact=0.1,
                            time_impact=2.0
                        ))
                    
                    if not clearance_available:
                        issues.append(ValidationIssue(
                            category=ValidationCategory.ASSEMBLY,
                            severity=ValidationSeverity.ERROR,
                            title="Insufficient Assembly Clearance",
                            description=f"Step {step_idx + 1}: Insufficient clearance for {part_name}",
                            affected_objects=[part_name],
                            recommendation="Increase clearances or modify part geometry",
                            cost_impact=0.3,
                            time_impact=4.0
                        ))
                        
        except Exception as e:
            logger.error(f"Assembly sequence validation failed: {e}")
            
        return issues

class CostValidator:
    """Validates cost implications of design decisions"""
    
    def __init__(self):
        self.material_costs = {  # USD per kg
            "aluminum": 2.0,
            "steel": 0.8,
            "stainless_steel": 4.0,
            "titanium": 30.0,
            "pla": 25.0,
            "abs": 30.0
        }
        
        self.process_costs = {  # USD per hour
            "fdm_3d_printing": 5.0,
            "sla_3d_printing": 15.0,
            "cnc_machining": 80.0,
            "injection_molding": 150.0
        }
        
    def estimate_material_cost(self, objects: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate material costs"""
        cost_analysis = {
            "total_cost": 0.0,
            "cost_breakdown": {},
            "cost_drivers": []
        }
        
        try:
            for obj_name, obj_data in objects.items():
                material = obj_data.get("material", "aluminum")
                volume = obj_data.get("volume", 0)  # cm³
                density = obj_data.get("density", 2.7)  # g/cm³ (aluminum default)
                
                mass = volume * density / 1000  # kg
                unit_cost = self.material_costs.get(material.lower(), 5.0)
                total_cost = mass * unit_cost
                
                cost_analysis["cost_breakdown"][obj_name] = {
                    "material": material,
                    "volume_cm3": volume,
                    "mass_kg": mass,
                    "unit_cost_per_kg": unit_cost,
                    "total_cost": total_cost
                }
                
                cost_analysis["total_cost"] += total_cost
                
                # Identify cost drivers
                if total_cost > cost_analysis["total_cost"] * 0.3:
                    cost_analysis["cost_drivers"].append({
                        "object": obj_name,
                        "cost": total_cost,
                        "reason": f"High material cost ({material})" if unit_cost > 10 else "Large volume"
                    })
                    
        except Exception as e:
            logger.error(f"Material cost estimation failed: {e}")
            cost_analysis["error"] = str(e)
            
        return cost_analysis
    
    def validate_cost_optimization(self, objects: Dict[str, Any], target_cost: float) -> List[ValidationIssue]:
        """Validate against target cost and suggest optimizations"""
        issues = []
        
        try:
            cost_analysis = self.estimate_material_cost(objects)
            actual_cost = cost_analysis["total_cost"]
            
            if actual_cost > target_cost:
                cost_ratio = actual_cost / target_cost
                severity = ValidationSeverity.CRITICAL if cost_ratio > 2.0 else ValidationSeverity.WARNING
                
                issues.append(ValidationIssue(
                    category=ValidationCategory.COST,
                    severity=severity,
                    title="Cost Target Exceeded",
                    description=f"Estimated cost ${actual_cost:.2f} exceeds target ${target_cost:.2f} by {(cost_ratio-1)*100:.0f}%",
                    affected_objects=list(objects.keys()),
                    recommendation="Consider material substitution, volume reduction, or design simplification",
                    cost_impact=actual_cost - target_cost
                ))
                
                # Suggest specific optimizations for cost drivers
                for driver in cost_analysis["cost_drivers"]:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.COST,
                        severity=ValidationSeverity.INFO,
                        title="Cost Optimization Opportunity",
                        description=f"{driver['object']}: ${driver['cost']:.2f} - {driver['reason']}",
                        affected_objects=[driver["object"]],
                        recommendation="Consider topology optimization or material substitution"
                    ))
                    
        except Exception as e:
            logger.error(f"Cost validation failed: {e}")
            
        return issues

class DesignValidationSystem:
    """Main design validation system coordinator"""
    
    def __init__(self):
        self.geometry_validator = GeometryValidator()
        self.manufacturing_validator = ManufacturingValidator()
        self.structural_validator = StructuralValidator()
        self.assembly_validator = AssemblyValidator()
        self.cost_validator = CostValidator()
        
        self.enabled_categories = {
            ValidationCategory.GEOMETRY: True,
            ValidationCategory.MANUFACTURING: True,
            ValidationCategory.STRUCTURAL: True,
            ValidationCategory.ASSEMBLY: True,
            ValidationCategory.COST: True,
            ValidationCategory.COMPLIANCE: False,
            ValidationCategory.SUSTAINABILITY: False
        }
        
    def validate_design(self, design_data: Dict[str, Any], 
                       validation_options: Dict[str, Any] = None) -> ValidationResult:
        """Perform comprehensive design validation"""
        
        if validation_options is None:
            validation_options = {}
            
        all_issues = []
        
        try:
            # Extract data components
            objects = design_data.get("objects", {})
            assemblies = design_data.get("assemblies", {})
            loads = design_data.get("loads", {})
            manufacturing_process = validation_options.get("manufacturing_process", "cnc_machining")
            target_cost = validation_options.get("target_cost", 100.0)
            
            # Geometry validation
            if self.enabled_categories[ValidationCategory.GEOMETRY]:
                all_issues.extend(self.geometry_validator.validate_wall_thickness(objects))
                all_issues.extend(self.geometry_validator.validate_feature_sizes(objects))
                all_issues.extend(self.geometry_validator.validate_hole_geometry(objects))
            
            # Manufacturing validation
            if self.enabled_categories[ValidationCategory.MANUFACTURING]:
                all_issues.extend(self.manufacturing_validator.validate_for_process(objects, manufacturing_process))
            
            # Structural validation
            if self.enabled_categories[ValidationCategory.STRUCTURAL]:
                all_issues.extend(self.structural_validator.validate_stress_concentrations(objects))
                if loads:
                    all_issues.extend(self.structural_validator.validate_load_paths(objects, loads))
            
            # Assembly validation
            if self.enabled_categories[ValidationCategory.ASSEMBLY] and assemblies:
                all_issues.extend(self.assembly_validator.validate_fit_tolerances(assemblies))
                all_issues.extend(self.assembly_validator.validate_assembly_sequence(assemblies))
            
            # Cost validation
            if self.enabled_categories[ValidationCategory.COST]:
                all_issues.extend(self.cost_validator.validate_cost_optimization(objects, target_cost))
            
            # Calculate overall metrics
            severity_counts = {s.value: 0 for s in ValidationSeverity}
            category_counts = {c.value: 0 for c in ValidationCategory}
            total_cost_impact = 0.0
            total_time_impact = 0.0
            
            for issue in all_issues:
                severity_counts[issue.severity.value] += 1
                category_counts[issue.category.value] += 1
                if issue.cost_impact:
                    total_cost_impact += issue.cost_impact
                if issue.time_impact:
                    total_time_impact += issue.time_impact
            
            # Calculate overall score (0-100)
            critical_weight = 50
            error_weight = 25
            warning_weight = 10
            info_weight = 1
            
            penalty = (
                severity_counts["critical"] * critical_weight +
                severity_counts["error"] * error_weight +
                severity_counts["warning"] * warning_weight +
                severity_counts["info"] * info_weight
            )
            
            overall_score = max(0, 100 - penalty)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(all_issues, overall_score)
            
            result = ValidationResult(
                timestamp=datetime.now(),
                overall_score=overall_score,
                total_issues=len(all_issues),
                issues_by_severity=severity_counts,
                issues_by_category=category_counts,
                issues=all_issues,
                recommendations=recommendations,
                estimated_cost_impact=total_cost_impact,
                estimated_time_impact=total_time_impact
            )
            
            logger.info(f"Design validation complete: {overall_score:.1f}/100, {len(all_issues)} issues")
            
        except Exception as e:
            logger.error(f"Design validation failed: {e}")
            result = ValidationResult(
                timestamp=datetime.now(),
                overall_score=0.0,
                total_issues=0,
                issues_by_severity={},
                issues_by_category={},
                issues=[],
                recommendations=[f"Validation failed: {e}"],
                estimated_cost_impact=0.0,
                estimated_time_impact=0.0
            )
            
        return result
    
    def _generate_recommendations(self, issues: List[ValidationIssue], overall_score: float) -> List[str]:
        """Generate high-level recommendations based on validation results"""
        recommendations = []
        
        try:
            # Count issues by category
            category_counts = {}
            for issue in issues:
                cat = issue.category.value
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            # Priority recommendations based on score
            if overall_score < 30:
                recommendations.append("🔴 Design requires major revision - multiple critical issues detected")
            elif overall_score < 60:
                recommendations.append("🟡 Design needs significant improvements before production")
            elif overall_score < 80:
                recommendations.append("🟢 Design is acceptable but optimization recommended")
            else:
                recommendations.append("✅ Design meets validation criteria")
            
            # Category-specific recommendations
            if category_counts.get("manufacturing", 0) > 3:
                recommendations.append("Focus on manufacturability - consider DFM guidelines")
            
            if category_counts.get("structural", 0) > 2:
                recommendations.append("Review structural design - add FEA analysis if needed")
            
            if category_counts.get("assembly", 0) > 2:
                recommendations.append("Optimize assembly process and tolerance stack-up")
            
            if category_counts.get("cost", 0) > 1:
                recommendations.append("Evaluate cost optimization opportunities")
            
            # Specific high-impact recommendations
            critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
            if critical_issues:
                recommendations.append(f"Address {len(critical_issues)} critical issues immediately")
            
            high_cost_issues = [i for i in issues if i.cost_impact and i.cost_impact > 0.3]
            if high_cost_issues:
                recommendations.append("Prioritize high-cost-impact issues for maximum ROI")
                
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            recommendations.append("Error generating recommendations - check validation logs")
            
        return recommendations
    
    def generate_validation_report(self, result: ValidationResult) -> str:
        """Generate comprehensive validation report"""
        try:
            report = f"""
# Design Validation Report

**Generated:** {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Overall Score:** {result.overall_score:.1f}/100

## Summary
- **Total Issues:** {result.total_issues}
- **Critical:** {result.issues_by_severity.get('critical', 0)}
- **Errors:** {result.issues_by_severity.get('error', 0)}
- **Warnings:** {result.issues_by_severity.get('warning', 0)}
- **Info:** {result.issues_by_severity.get('info', 0)}

**Estimated Impact:**
- **Cost Impact:** ${result.estimated_cost_impact:.2f}
- **Time Impact:** {result.estimated_time_impact:.1f} hours

## Issues by Category
"""
            
            for category in ValidationCategory:
                count = result.issues_by_category.get(category.value, 0)
                if count > 0:
                    report += f"- **{category.value.title()}:** {count} issues\n"
            
            report += "\n## Detailed Issues\n"
            
            # Group issues by severity
            for severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR, 
                           ValidationSeverity.WARNING, ValidationSeverity.INFO]:
                severity_issues = [i for i in result.issues if i.severity == severity]
                
                if severity_issues:
                    report += f"\n### {severity.value.upper()} ({len(severity_issues)} issues)\n"
                    
                    for issue in severity_issues:
                        report += f"\n**{issue.title}**\n"
                        report += f"- *Category:* {issue.category.value}\n"
                        report += f"- *Objects:* {', '.join(issue.affected_objects)}\n"
                        report += f"- *Description:* {issue.description}\n"
                        
                        if issue.location:
                            report += f"- *Location:* ({issue.location[0]:.1f}, {issue.location[1]:.1f}, {issue.location[2]:.1f})\n"
                        
                        if issue.recommendation:
                            report += f"- *Recommendation:* {issue.recommendation}\n"
                        
                        if issue.cost_impact:
                            report += f"- *Cost Impact:* ${issue.cost_impact:.2f}\n"
                        
                        if issue.time_impact:
                            report += f"- *Time Impact:* {issue.time_impact:.1f} hours\n"
            
            report += "\n## Recommendations\n"
            for i, rec in enumerate(result.recommendations, 1):
                report += f"{i}. {rec}\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate validation report: {e}")
            return f"Error generating validation report: {e}"

# Utility functions for creating validation test data

def create_mock_design_data() -> Dict[str, Any]:
    """Create mock design data for testing validation"""
    return {
        "objects": {
            "housing": {
                "material": "aluminum",
                "volume": 125.0,  # cm³
                "density": 2.7,   # g/cm³
                "faces": [
                    {"thickness": 1.2, "center": (0, 0, 0)},
                    {"thickness": 0.6, "center": (10, 0, 0)}  # Thin wall
                ],
                "holes": [
                    {"diameter": 6.0, "depth": 30.0, "position": (5, 5, 0)},
                    {"diameter": 0.8, "depth": 5.0, "position": (15, 5, 0)}  # Small hole
                ],
                "stress_concentrations": [
                    {"concentration_factor": 4.2, "location": (0, 10, 0)}
                ]
            }
        },
        "assemblies": {
            "main_assembly": {
                "fits": [
                    {
                        "type": "clearance",
                        "shaft_tolerance": "g6",
                        "hole_tolerance": "H7",
                        "nominal_size": 25,
                        "shaft_part": "shaft",
                        "hole_part": "housing"
                    }
                ]
            }
        },
        "loads": {
            "main_load": {
                "magnitude": 1000.0,  # N
                "point": (0, 0, 10),
                "supports": ["support1"],
                "cross_section_area": 50e-6,  # m²
                "affected_objects": ["housing"]
            }
        }
    }