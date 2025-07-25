"""
Enhanced Manufacturing Framework for FreeCAD
============================================

This module provides comprehensive manufacturing constraints, tolerances,
and process-specific design rules for accurate CAD modeling with real-world
manufacturing considerations.
"""

import math
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum


class ManufacturingProcess(Enum):
    """Manufacturing process types with specific constraints"""
    FDM = "fdm"  # Fused Deposition Modeling
    SLA = "sla"  # Stereolithography
    SLS = "sls"  # Selective Laser Sintering
    DMLS = "dmls"  # Direct Metal Laser Sintering
    CNC_MILLING = "cnc_milling"
    CNC_TURNING = "cnc_turning"
    INJECTION_MOLDING = "injection_molding"
    CASTING = "casting"
    SHEET_METAL = "sheet_metal"
    MACHINING = "machining"


class ToleranceGrade(Enum):
    """ISO tolerance grades"""
    IT01 = 0.3  # Precision gauge blocks
    IT0 = 0.5   # Precision gauge blocks
    IT1 = 0.8   # High precision applications
    IT2 = 1.2   # High precision applications
    IT3 = 2.0   # High precision applications
    IT4 = 3.0   # High precision applications
    IT5 = 4.0   # High precision applications
    IT6 = 6.0   # Precision applications
    IT7 = 10.0  # General precision
    IT8 = 14.0  # General precision
    IT9 = 25.0  # General machining
    IT10 = 40.0 # General machining
    IT11 = 60.0 # Rough machining
    IT12 = 100.0 # Rough machining


class FitType(Enum):
    """Standard fit types for mating parts"""
    CLEARANCE = "clearance"  # Always clearance
    TRANSITION = "transition"  # May be clearance or interference
    INTERFERENCE = "interference"  # Always interference


@dataclass
class Material:
    """Material properties for manufacturing analysis"""
    name: str
    density: float  # kg/m³
    tensile_strength: float  # MPa
    yield_strength: float  # MPa
    elastic_modulus: float  # GPa
    poisson_ratio: float
    thermal_expansion: float  # 1/K
    melting_point: Optional[float] = None  # °C
    glass_transition: Optional[float] = None  # °C
    surface_roughness_ra: float = 1.6  # μm
    cost_per_kg: float = 0.0  # USD
    recyclable: bool = True
    food_safe: bool = False
    
    # Process-specific properties
    printable_processes: List[ManufacturingProcess] = field(default_factory=list)
    machinable_processes: List[ManufacturingProcess] = field(default_factory=list)


@dataclass
class ProcessConstraints:
    """Manufacturing process constraints and capabilities"""
    process: ManufacturingProcess
    min_feature_size: float  # mm
    max_feature_size: float  # mm
    min_wall_thickness: float  # mm
    max_wall_thickness: float  # mm
    min_hole_diameter: float  # mm
    max_overhang_angle: float  # degrees
    support_required_angle: float  # degrees
    layer_height: Optional[float] = None  # mm (for additive)
    surface_roughness_ra: Tuple[float, float] = (0.8, 25.0)  # μm (min, max)
    dimensional_accuracy: float = 0.1  # mm
    minimum_draft_angle: float = 0.0  # degrees
    tolerance_grade: ToleranceGrade = ToleranceGrade.IT9
    cost_setup: float = 0.0  # USD
    cost_per_volume: float = 0.0  # USD/cm³
    cost_per_area: float = 0.0  # USD/cm²
    build_volume: Optional[Tuple[float, float, float]] = None  # mm (x, y, z)


class ManufacturingDatabase:
    """Database of materials and process constraints"""
    
    def __init__(self):
        self.materials = self._load_materials()
        self.processes = self._load_process_constraints()
        
    def _load_materials(self) -> Dict[str, Material]:
        """Load material database"""
        materials = {}
        
        # Common 3D printing materials
        materials["PLA"] = Material(
            name="PLA",
            density=1240,
            tensile_strength=50,
            yield_strength=60,
            elastic_modulus=3.5,
            poisson_ratio=0.36,
            thermal_expansion=70e-6,
            glass_transition=60,
            surface_roughness_ra=6.3,
            cost_per_kg=25,
            food_safe=True,
            printable_processes=[ManufacturingProcess.FDM]
        )
        
        materials["ABS"] = Material(
            name="ABS",
            density=1040,
            tensile_strength=40,
            yield_strength=38,
            elastic_modulus=2.0,
            poisson_ratio=0.35,
            thermal_expansion=90e-6,
            glass_transition=105,
            surface_roughness_ra=6.3,
            cost_per_kg=20,
            printable_processes=[ManufacturingProcess.FDM]
        )
        
        materials["PETG"] = Material(
            name="PETG",
            density=1270,
            tensile_strength=50,
            yield_strength=50,
            elastic_modulus=2.0,
            poisson_ratio=0.38,
            thermal_expansion=65e-6,
            glass_transition=85,
            surface_roughness_ra=3.2,
            cost_per_kg=30,
            food_safe=True,
            printable_processes=[ManufacturingProcess.FDM]
        )
        
        # Resin materials
        materials["Standard_Resin"] = Material(
            name="Standard Resin",
            density=1100,
            tensile_strength=65,
            yield_strength=55,
            elastic_modulus=2.8,
            poisson_ratio=0.41,
            thermal_expansion=80e-6,
            surface_roughness_ra=0.8,
            cost_per_kg=80,
            printable_processes=[ManufacturingProcess.SLA]
        )
        
        # Metal materials
        materials["Aluminum_6061"] = Material(
            name="Aluminum 6061",
            density=2700,
            tensile_strength=310,
            yield_strength=276,
            elastic_modulus=69,
            poisson_ratio=0.33,
            thermal_expansion=23.6e-6,
            melting_point=660,
            surface_roughness_ra=1.6,
            cost_per_kg=4,
            machinable_processes=[ManufacturingProcess.CNC_MILLING, ManufacturingProcess.CNC_TURNING]
        )
        
        materials["Steel_1018"] = Material(
            name="Steel 1018",
            density=7870,
            tensile_strength=440,
            yield_strength=370,
            elastic_modulus=200,
            poisson_ratio=0.29,
            thermal_expansion=11.7e-6,
            melting_point=1420,
            surface_roughness_ra=3.2,
            cost_per_kg=1.5,
            machinable_processes=[ManufacturingProcess.CNC_MILLING, ManufacturingProcess.CNC_TURNING]
        )
        
        materials["Stainless_316L"] = Material(
            name="Stainless Steel 316L",
            density=8000,
            tensile_strength=580,
            yield_strength=290,
            elastic_modulus=200,
            poisson_ratio=0.27,
            thermal_expansion=16e-6,
            melting_point=1400,
            surface_roughness_ra=1.6,
            cost_per_kg=8,
            food_safe=True,
            printable_processes=[ManufacturingProcess.DMLS],
            machinable_processes=[ManufacturingProcess.CNC_MILLING, ManufacturingProcess.CNC_TURNING]
        )
        
        return materials
    
    def _load_process_constraints(self) -> Dict[ManufacturingProcess, ProcessConstraints]:
        """Load manufacturing process constraints"""
        processes = {}
        
        # FDM 3D Printing
        processes[ManufacturingProcess.FDM] = ProcessConstraints(
            process=ManufacturingProcess.FDM,
            min_feature_size=0.4,
            max_feature_size=300,
            min_wall_thickness=0.8,
            max_wall_thickness=50,
            min_hole_diameter=0.5,
            max_overhang_angle=45,
            support_required_angle=60,
            layer_height=0.2,
            surface_roughness_ra=(6.3, 25),
            dimensional_accuracy=0.2,
            tolerance_grade=ToleranceGrade.IT12,
            cost_setup=0,
            cost_per_volume=0.50,
            build_volume=(200, 200, 200)
        )
        
        # SLA 3D Printing
        processes[ManufacturingProcess.SLA] = ProcessConstraints(
            process=ManufacturingProcess.SLA,
            min_feature_size=0.1,
            max_feature_size=150,
            min_wall_thickness=0.4,
            max_wall_thickness=50,
            min_hole_diameter=0.2,
            max_overhang_angle=30,
            support_required_angle=45,
            layer_height=0.05,
            surface_roughness_ra=(0.8, 3.2),
            dimensional_accuracy=0.05,
            tolerance_grade=ToleranceGrade.IT9,
            cost_setup=5,
            cost_per_volume=2.00,
            build_volume=(150, 150, 150)
        )
        
        # SLS 3D Printing
        processes[ManufacturingProcess.SLS] = ProcessConstraints(
            process=ManufacturingProcess.SLS,
            min_feature_size=0.3,
            max_feature_size=300,
            min_wall_thickness=0.7,
            max_wall_thickness=50,
            min_hole_diameter=0.5,
            max_overhang_angle=90,  # No supports needed
            support_required_angle=90,
            layer_height=0.1,
            surface_roughness_ra=(3.2, 12.5),
            dimensional_accuracy=0.1,
            tolerance_grade=ToleranceGrade.IT10,
            cost_setup=50,
            cost_per_volume=5.00,
            build_volume=(300, 300, 300)
        )
        
        # CNC Milling
        processes[ManufacturingProcess.CNC_MILLING] = ProcessConstraints(
            process=ManufacturingProcess.CNC_MILLING,
            min_feature_size=0.1,
            max_feature_size=2000,
            min_wall_thickness=0.5,
            max_wall_thickness=200,
            min_hole_diameter=0.5,
            max_overhang_angle=90,
            support_required_angle=90,
            surface_roughness_ra=(0.4, 6.3),
            dimensional_accuracy=0.02,
            minimum_draft_angle=0.5,
            tolerance_grade=ToleranceGrade.IT7,
            cost_setup=100,
            cost_per_volume=15.00,
            build_volume=(1000, 500, 300)
        )
        
        # DMLS (Metal 3D Printing)
        processes[ManufacturingProcess.DMLS] = ProcessConstraints(
            process=ManufacturingProcess.DMLS,
            min_feature_size=0.2,
            max_feature_size=200,
            min_wall_thickness=0.4,
            max_wall_thickness=50,
            min_hole_diameter=0.3,
            max_overhang_angle=45,
            support_required_angle=45,
            layer_height=0.03,
            surface_roughness_ra=(6.3, 25),
            dimensional_accuracy=0.1,
            tolerance_grade=ToleranceGrade.IT9,
            cost_setup=200,
            cost_per_volume=50.00,
            build_volume=(250, 250, 300)
        )
        
        return processes


class ToleranceCalculator:
    """Calculate tolerances and fits for manufacturing"""
    
    @staticmethod
    def calculate_tolerance(nominal_size: float, grade: ToleranceGrade) -> float:
        """Calculate tolerance for given nominal size and grade"""
        if nominal_size <= 3:
            i = 0.45 * (nominal_size ** (1/3)) + 0.001 * nominal_size
        elif nominal_size <= 6:
            i = 0.45 * (nominal_size ** (1/3)) + 0.001 * nominal_size
        elif nominal_size <= 10:
            i = 0.45 * (nominal_size ** (1/3)) + 0.001 * nominal_size
        elif nominal_size <= 18:
            i = 0.45 * (nominal_size ** (1/3)) + 0.001 * nominal_size
        elif nominal_size <= 30:
            i = 0.45 * (nominal_size ** (1/3)) + 0.001 * nominal_size
        elif nominal_size <= 50:
            i = 0.45 * (nominal_size ** (1/3)) + 0.001 * nominal_size
        elif nominal_size <= 80:
            i = 0.45 * (nominal_size ** (1/3)) + 0.001 * nominal_size
        elif nominal_size <= 120:
            i = 0.45 * (nominal_size ** (1/3)) + 0.001 * nominal_size
        elif nominal_size <= 180:
            i = 0.45 * (nominal_size ** (1/3)) + 0.001 * nominal_size
        elif nominal_size <= 250:
            i = 0.45 * (nominal_size ** (1/3)) + 0.001 * nominal_size
        else:
            i = 0.45 * (nominal_size ** (1/3)) + 0.001 * nominal_size
            
        return i * grade.value / 1000  # Convert to mm
    
    @staticmethod
    def calculate_fit(hole_size: float, shaft_size: float, fit_type: FitType, 
                     tolerance_grade: ToleranceGrade = ToleranceGrade.IT7) -> Dict[str, float]:
        """Calculate fit parameters for hole-shaft combination"""
        hole_tolerance = ToleranceCalculator.calculate_tolerance(hole_size, tolerance_grade)
        shaft_tolerance = ToleranceCalculator.calculate_tolerance(shaft_size, tolerance_grade)
        
        if fit_type == FitType.CLEARANCE:
            # H7/g6 fit example
            hole_upper = hole_size + hole_tolerance
            hole_lower = hole_size
            shaft_upper = shaft_size - 0.01  # Fundamental deviation
            shaft_lower = shaft_size - 0.01 - shaft_tolerance
            
        elif fit_type == FitType.TRANSITION:
            # H7/k6 fit example
            hole_upper = hole_size + hole_tolerance
            hole_lower = hole_size
            shaft_upper = shaft_size + 0.005  # Small interference
            shaft_lower = shaft_size + 0.005 - shaft_tolerance
            
        elif fit_type == FitType.INTERFERENCE:
            # H7/p6 fit example
            hole_upper = hole_size + hole_tolerance
            hole_lower = hole_size
            shaft_upper = shaft_size + 0.02  # Significant interference
            shaft_lower = shaft_size + 0.02 - shaft_tolerance
        
        clearance_max = hole_upper - shaft_lower
        clearance_min = hole_lower - shaft_upper
        
        return {
            "hole_upper": hole_upper,
            "hole_lower": hole_lower,
            "shaft_upper": shaft_upper,
            "shaft_lower": shaft_lower,
            "clearance_max": clearance_max,
            "clearance_min": clearance_min,
            "fit_type": fit_type.value
        }


class DesignRuleChecker:
    """Check design against manufacturing constraints"""
    
    def __init__(self, process: ManufacturingProcess, material: str):
        self.db = ManufacturingDatabase()
        self.process_constraints = self.db.processes[process]
        self.material = self.db.materials.get(material)
        self.violations = []
        
    def check_feature_size(self, feature_size: float, feature_name: str = "feature") -> bool:
        """Check if feature size is within process limits"""
        constraints = self.process_constraints
        
        if feature_size < constraints.min_feature_size:
            self.violations.append(
                f"{feature_name} size {feature_size:.3f}mm is below minimum "
                f"{constraints.min_feature_size:.3f}mm for {self.process_constraints.process.value}"
            )
            return False
            
        if feature_size > constraints.max_feature_size:
            self.violations.append(
                f"{feature_name} size {feature_size:.3f}mm exceeds maximum "
                f"{constraints.max_feature_size:.3f}mm for {self.process_constraints.process.value}"
            )
            return False
            
        return True
    
    def check_wall_thickness(self, thickness: float, feature_name: str = "wall") -> bool:
        """Check wall thickness against process constraints"""
        constraints = self.process_constraints
        
        if thickness < constraints.min_wall_thickness:
            self.violations.append(
                f"{feature_name} thickness {thickness:.3f}mm is below minimum "
                f"{constraints.min_wall_thickness:.3f}mm for {self.process_constraints.process.value}"
            )
            return False
            
        if thickness > constraints.max_wall_thickness:
            self.violations.append(
                f"{feature_name} thickness {thickness:.3f}mm exceeds maximum "
                f"{constraints.max_wall_thickness:.3f}mm for {self.process_constraints.process.value}"
            )
            return False
            
        return True
    
    def check_overhang_angle(self, angle: float, feature_name: str = "overhang") -> bool:
        """Check overhang angle against process constraints"""
        constraints = self.process_constraints
        
        if angle > constraints.max_overhang_angle:
            if angle > constraints.support_required_angle:
                self.violations.append(
                    f"{feature_name} angle {angle:.1f}° exceeds maximum unsupported "
                    f"{constraints.max_overhang_angle:.1f}° - supports required"
                )
            else:
                self.violations.append(
                    f"{feature_name} angle {angle:.1f}° may require supports "
                    f"(max unsupported: {constraints.max_overhang_angle:.1f}°)"
                )
            return False
            
        return True
    
    def check_hole_diameter(self, diameter: float, feature_name: str = "hole") -> bool:
        """Check hole diameter against process constraints"""
        constraints = self.process_constraints
        
        if diameter < constraints.min_hole_diameter:
            self.violations.append(
                f"{feature_name} diameter {diameter:.3f}mm is below minimum "
                f"{constraints.min_hole_diameter:.3f}mm for {self.process_constraints.process.value}"
            )
            return False
            
        return True
    
    def check_build_volume(self, dimensions: Tuple[float, float, float]) -> bool:
        """Check if part fits within build volume"""
        constraints = self.process_constraints
        
        if not constraints.build_volume:
            return True  # No build volume constraint
            
        x, y, z = dimensions
        max_x, max_y, max_z = constraints.build_volume
        
        violations_found = False
        
        if x > max_x:
            self.violations.append(
                f"Part X dimension {x:.1f}mm exceeds build volume {max_x:.1f}mm"
            )
            violations_found = True
            
        if y > max_y:
            self.violations.append(
                f"Part Y dimension {y:.1f}mm exceeds build volume {max_y:.1f}mm"
            )
            violations_found = True
            
        if z > max_z:
            self.violations.append(
                f"Part Z dimension {z:.1f}mm exceeds build volume {max_z:.1f}mm"
            )
            violations_found = True
            
        return not violations_found
    
    def get_violations(self) -> List[str]:
        """Return list of design rule violations"""
        return self.violations.copy()
    
    def clear_violations(self):
        """Clear violation list"""
        self.violations.clear()


class CostEstimator:
    """Estimate manufacturing costs"""
    
    def __init__(self, process: ManufacturingProcess, material: str):
        self.db = ManufacturingDatabase()
        self.process_constraints = self.db.processes[process]
        self.material = self.db.materials.get(material)
        
    def estimate_cost(self, volume_cm3: float, surface_area_cm2: float, 
                     quantity: int = 1, complexity_factor: float = 1.0) -> Dict[str, float]:
        """Estimate manufacturing cost breakdown"""
        constraints = self.process_constraints
        material = self.material
        
        # Material cost
        if material:
            volume_m3 = volume_cm3 / 1e6
            mass_kg = volume_m3 * material.density
            material_cost = mass_kg * material.cost_per_kg
        else:
            material_cost = 0
            mass_kg = 0
            
        # Setup cost (one-time)
        setup_cost = constraints.cost_setup
        
        # Manufacturing cost
        volume_cost = volume_cm3 * constraints.cost_per_volume * complexity_factor
        area_cost = surface_area_cm2 * constraints.cost_per_area
        manufacturing_cost = volume_cost + area_cost
        
        # Total cost per unit
        cost_per_unit = material_cost + manufacturing_cost
        setup_cost_per_unit = setup_cost / quantity if quantity > 0 else setup_cost
        
        total_cost_per_unit = cost_per_unit + setup_cost_per_unit
        total_cost = total_cost_per_unit * quantity + setup_cost
        
        return {
            "material_cost_per_unit": material_cost,
            "manufacturing_cost_per_unit": manufacturing_cost,
            "setup_cost": setup_cost,
            "setup_cost_per_unit": setup_cost_per_unit,
            "cost_per_unit": cost_per_unit,
            "total_cost_per_unit": total_cost_per_unit,
            "total_cost": total_cost,
            "quantity": quantity,
            "volume_cm3": volume_cm3,
            "surface_area_cm2": surface_area_cm2,
            "mass_kg": mass_kg
        }


class ManufacturingOptimizer:
    """Optimize designs for manufacturing"""
    
    def __init__(self):
        self.db = ManufacturingDatabase()
        
    def suggest_process(self, requirements: Dict[str, Any]) -> List[Tuple[ManufacturingProcess, float]]:
        """Suggest best manufacturing processes based on requirements"""
        suggestions = []
        
        for process, constraints in self.db.processes.items():
            score = self._score_process(process, constraints, requirements)
            if score > 0:
                suggestions.append((process, score))
                
        # Sort by score (higher is better)
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions
    
    def _score_process(self, process: ManufacturingProcess, 
                      constraints: ProcessConstraints, 
                      requirements: Dict[str, Any]) -> float:
        """Score how well a process meets requirements"""
        score = 100.0  # Start with perfect score
        
        # Check dimensional requirements
        if "dimensions" in requirements:
            dims = requirements["dimensions"]
            max_dim = max(dims)
            
            if constraints.build_volume:
                max_build = max(constraints.build_volume)
                if max_dim > max_build:
                    return 0  # Cannot manufacture
                    
        # Check tolerance requirements
        if "tolerance" in requirements:
            req_tolerance = requirements["tolerance"]
            process_tolerance = constraints.dimensional_accuracy
            
            if process_tolerance > req_tolerance:
                score *= 0.5  # Process not accurate enough
                
        # Check surface finish requirements
        if "surface_roughness" in requirements:
            req_roughness = requirements["surface_roughness"]
            min_roughness, max_roughness = constraints.surface_roughness_ra
            
            if req_roughness < min_roughness:
                score *= 0.7  # Process too rough
                
        # Check quantity requirements
        if "quantity" in requirements:
            quantity = requirements["quantity"]
            
            # Additive processes better for low quantities
            if process in [ManufacturingProcess.FDM, ManufacturingProcess.SLA, 
                          ManufacturingProcess.SLS, ManufacturingProcess.DMLS]:
                if quantity < 100:
                    score *= 1.2
                else:
                    score *= 0.8
                    
            # Traditional processes better for high quantities
            else:
                if quantity > 100:
                    score *= 1.2
                else:
                    score *= 0.8
                    
        # Check material compatibility
        if "material" in requirements:
            material_name = requirements["material"]
            material = self.db.materials.get(material_name)
            
            if material:
                if process in material.printable_processes or process in material.machinable_processes:
                    score *= 1.1
                else:
                    score *= 0.3  # Material not compatible
                    
        return max(0, score)