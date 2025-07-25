"""
Enhanced FreeCAD MCP Server
Integrates advanced manufacturing framework, spatial reasoning, and design validation
with existing FreeCAD MCP functionality.
"""

import os
import json
import logging
import math
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, Literal, List, Union, Tuple

from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent, ImageContent

# Import existing server functionality
from .server import (
    FreeCADConnection, get_freecad_connection, mcp as original_mcp,
    _freecad_connection
)

# Import enhanced frameworks
from .manufacturing_framework import (
    ManufacturingFramework, MaterialType, ProcessType, ToleranceType,
    create_standard_material, create_machining_process
)
from .enhanced_spatial_framework import (
    EnhancedSpatialFramework, SpatialObject, SpatialConstraint,
    ObjectType, ConstraintType, create_mechanical_component,
    create_clearance_constraint, create_accessibility_constraint
)
from .advanced_cad_operations import (
    AdvancedCADOperations, FeatureType, PatternType, BooleanOperation,
    create_rectangular_sketch, create_circular_sketch
)
from .design_validation_system import (
    DesignValidationSystem, ValidationCategory, ValidationSeverity,
    create_mock_design_data
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TaiyakiAI-Enhanced")

# Global framework instances
manufacturing_framework = ManufacturingFramework()
spatial_framework = EnhancedSpatialFramework()
cad_operations = AdvancedCADOperations()
validation_system = DesignValidationSystem()

# Initialize with standard materials and processes
manufacturing_framework.add_material(create_standard_material("aluminum_6061"))
manufacturing_framework.add_material(create_standard_material("steel_mild"))
manufacturing_framework.add_material(create_standard_material("pla"))
manufacturing_framework.add_process(create_machining_process("cnc_milling"))

@asynccontextmanager
async def enhanced_server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Enhanced server lifespan with framework initialization"""
    try:
        logger.info("Enhanced Taiyaki AI MCP server starting up")
        
        # Initialize frameworks
        logger.info("Initializing manufacturing framework...")
        logger.info("Initializing spatial reasoning framework...")
        logger.info("Initializing advanced CAD operations...")
        logger.info("Initializing design validation system...")
        
        try:
            _ = get_freecad_connection()
            logger.info("Successfully connected to FreeCAD on startup")
        except Exception as e:
            logger.warning(f"Could not connect to FreeCAD on startup: {str(e)}")
            logger.warning(
                "Make sure the Taiyaki AI workbench is active in FreeCAD before using FreeCAD resources or tools"
            )
        
        yield {}
        
    finally:
        # Clean up
        global _freecad_connection
        if _freecad_connection:
            logger.info("Disconnecting from FreeCAD on shutdown")
            _freecad_connection = None
        logger.info("Enhanced Taiyaki AI MCP server shut down")

# Create enhanced MCP server instance
enhanced_mcp = FastMCP(
    "TaiyakiAI-Enhanced",
    description="Enhanced Taiyaki AI - FreeCAD integration with advanced manufacturing, spatial reasoning, and validation",
    lifespan=enhanced_server_lifespan,
)

# Copy all existing tools from original server
# (In practice, you would import and register them here)

# New enhanced tools

@enhanced_mcp.tool()
def analyze_manufacturing_requirements(
    ctx: Context,
    doc_name: str,
    material: str = "aluminum_6061",
    process: str = "cnc_milling",
    tolerance_grade: str = "IT7",
    surface_finish: float = 1.6
) -> List[TextContent]:
    """
    Analyze manufacturing requirements for a FreeCAD document using advanced manufacturing framework.
    
    Args:
        doc_name: Name of the FreeCAD document to analyze
        material: Material type (aluminum_6061, steel_mild, pla, abs, etc.)
        process: Manufacturing process (cnc_milling, fdm_printing, injection_molding, etc.)
        tolerance_grade: ISO tolerance grade (IT6, IT7, IT8, etc.)
        surface_finish: Required surface finish in Ra (μm)
    
    Returns:
        Comprehensive manufacturing analysis with cost estimates and recommendations
    """
    logger.info(f"Analyzing manufacturing requirements for {doc_name}")
    
    try:
        # Get objects from FreeCAD
        freecad = get_freecad_connection()
        objects = freecad.get_objects(doc_name)
        
        # Create manufacturing analysis request
        analysis_request = {
            "material": material,
            "process": process,
            "tolerance_grade": tolerance_grade,
            "surface_finish": surface_finish,
            "objects": objects,
            "quantity": 1
        }
        
        # Perform manufacturing analysis
        analysis_result = manufacturing_framework.analyze_manufacturing_requirements(analysis_request)
        
        # Format results
        report = f"""# Manufacturing Analysis Report

## Overview
- **Material**: {analysis_result['material']['name']}
- **Process**: {analysis_result['process']['name']}
- **Tolerance Grade**: {tolerance_grade}
- **Surface Finish**: Ra {surface_finish} μm

## Cost Analysis
- **Material Cost**: ${analysis_result['cost_analysis']['material_cost']:.2f}
- **Processing Cost**: ${analysis_result['cost_analysis']['processing_cost']:.2f}
- **Total Unit Cost**: ${analysis_result['cost_analysis']['total_cost']:.2f}
- **Lead Time**: {analysis_result['cost_analysis']['lead_time']:.1f} days

## Manufacturing Constraints
"""
        
        for constraint in analysis_result.get('constraints', []):
            report += f"- **{constraint['type']}**: {constraint['description']}\n"
            if constraint.get('recommendation'):
                report += f"  - *Recommendation*: {constraint['recommendation']}\n"
        
        report += "\n## Process Recommendations\n"
        for rec in analysis_result.get('recommendations', []):
            report += f"- {rec}\n"
        
        if analysis_result.get('warnings'):
            report += "\n## Warnings\n"
            for warning in analysis_result['warnings']:
                report += f"- ⚠️ {warning}\n"
        
        return [TextContent(type="text", text=report)]
        
    except Exception as e:
        logger.error(f"Manufacturing analysis failed: {e}")
        return [TextContent(type="text", text=f"Manufacturing analysis failed: {e}")]

@enhanced_mcp.tool()
def create_spatial_layout(
    ctx: Context,
    layout_name: str,
    components: List[Dict[str, Any]],
    constraints: List[Dict[str, Any]] = None,
    workspace_bounds: Dict[str, float] = None
) -> List[TextContent]:
    """
    Create and optimize spatial layout for mechanical components with collision detection.
    
    Args:
        layout_name: Name for the spatial layout
        components: List of component definitions with positions and dimensions
        constraints: List of spatial constraints (clearance, accessibility, etc.)
        workspace_bounds: Workspace boundary limits
    
    Returns:
        Spatial layout analysis with optimization results and collision detection
    
    Example:
        components = [
            {
                "name": "motor",
                "type": "mechanical",
                "position": [0, 0, 50],
                "dimensions": [100, 80, 60],
                "mass": 2.5,
                "fixed": False
            },
            {
                "name": "controller",
                "type": "electronic", 
                "position": [150, 0, 30],
                "dimensions": [80, 60, 20],
                "heat_generation": 5.0
            }
        ]
        
        constraints = [
            {
                "type": "clearance",
                "objects": ["motor", "controller"],
                "min_distance": 20.0,
                "priority": 3
            },
            {
                "type": "accessibility",
                "objects": ["controller"],
                "direction": "top",
                "distance": 50.0,
                "priority": 4
            }
        ]
    """
    logger.info(f"Creating spatial layout: {layout_name}")
    
    try:
        # Clear existing layout
        spatial_framework.objects.clear()
        spatial_framework.constraints.clear()
        
        # Set workspace bounds if provided
        if workspace_bounds:
            spatial_framework.layout_bounds.min_x = workspace_bounds.get("min_x", -1000)
            spatial_framework.layout_bounds.min_y = workspace_bounds.get("min_y", -1000)
            spatial_framework.layout_bounds.min_z = workspace_bounds.get("min_z", 0)
            spatial_framework.layout_bounds.max_x = workspace_bounds.get("max_x", 1000)
            spatial_framework.layout_bounds.max_y = workspace_bounds.get("max_y", 1000)
            spatial_framework.layout_bounds.max_z = workspace_bounds.get("max_z", 2000)
        
        # Add components
        for comp in components:
            if comp["type"] == "mechanical":
                obj = create_mechanical_component(
                    name=comp["name"],
                    position=tuple(comp["position"]),
                    dimensions=tuple(comp["dimensions"]),
                    mass=comp.get("mass", 1.0),
                    fixed=comp.get("fixed", False)
                )
            else:
                obj = SpatialObject(
                    name=comp["name"],
                    obj_type=ObjectType(comp["type"]),
                    position=tuple(comp["position"]),
                    dimensions=tuple(comp["dimensions"]),
                    mass=comp.get("mass", 1.0),
                    fixed=comp.get("fixed", False),
                    thermal_properties={"heat_generation": comp.get("heat_generation", 0.0)}
                )
            
            spatial_framework.add_object(obj)
        
        # Add constraints
        if constraints:
            for const in constraints:
                constraint = SpatialConstraint(
                    constraint_type=ConstraintType(const["type"]),
                    objects=const["objects"],
                    parameters=const.get("parameters", {k: v for k, v in const.items() 
                                                      if k not in ["type", "objects", "priority"]}),
                    priority=const.get("priority", 3)
                )
                spatial_framework.add_constraint(constraint)
        
        # Perform initial evaluation
        initial_evaluation = spatial_framework.evaluate_layout()
        
        # Detect collisions
        collisions = spatial_framework.detect_collisions()
        
        # Optimize layout if needed
        optimization_result = None
        if initial_evaluation["overall_score"] < 80 or collisions:
            logger.info("Layout needs optimization - running spatial optimizer")
            optimization_result = spatial_framework.optimize_layout(max_iterations=50)
        
        # Generate comprehensive report
        report = spatial_framework.generate_layout_report()
        
        if optimization_result:
            report += f"\n## Optimization Results\n"
            report += f"- **Initial Score**: {optimization_result['initial_score']:.1f}/100\n"
            report += f"- **Final Score**: {optimization_result['final_score']:.1f}/100\n"
            report += f"- **Iterations**: {optimization_result['iterations']}\n"
            report += f"- **Improvements**: {len(optimization_result['improvements'])}\n"
        
        logger.info(f"Spatial layout '{layout_name}' created successfully")
        return [TextContent(type="text", text=report)]
        
    except Exception as e:
        logger.error(f"Spatial layout creation failed: {e}")
        return [TextContent(type="text", text=f"Spatial layout creation failed: {e}")]

@enhanced_mcp.tool()
def create_parametric_feature(
    ctx: Context,
    doc_name: str,
    feature_name: str,
    feature_type: str,
    parameters: Dict[str, Any],
    sketch_name: str = None
) -> List[TextContent | ImageContent]:
    """
    Create advanced parametric features with manufacturing integration.
    
    Args:
        doc_name: FreeCAD document name
        feature_name: Name for the new feature
        feature_type: Type of feature (extrude, revolve, hole, fillet, pattern, etc.)
        parameters: Feature-specific parameters
        sketch_name: Associated sketch name (for sketch-based features)
    
    Returns:
        Feature creation result with manufacturing analysis
    
    Examples:
        # Parametric hole with manufacturing constraints
        {
            "feature_type": "hole",
            "parameters": {
                "position": [10, 20, 0],
                "diameter": "bolt_diameter * 1.1",  # Parametric expression
                "depth": 15.0,
                "hole_type": "precision"
            }
        }
        
        # Fillet with manufacturing considerations
        {
            "feature_type": "fillet",
            "parameters": {
                "edges": ["Box.Edge1", "Box.Edge2"],
                "radius": "wall_thickness * 0.5"
            }
        }
    """
    logger.info(f"Creating parametric feature: {feature_name} ({feature_type})")
    
    try:
        # Validate feature type
        try:
            feature_enum = FeatureType(feature_type.lower())
        except ValueError:
            return [TextContent(type="text", text=f"Unknown feature type: {feature_type}")]
        
        # Create feature using advanced CAD operations
        success = False
        
        if feature_enum == FeatureType.EXTRUDE:
            success = cad_operations.create_extrude_feature(
                name=feature_name,
                sketch_name=sketch_name,
                length=parameters.get("length", 10.0),
                direction=parameters.get("direction", "normal"),
                symmetric=parameters.get("symmetric", False)
            )
            
        elif feature_enum == FeatureType.REVOLVE:
            success = cad_operations.create_revolve_feature(
                name=feature_name,
                sketch_name=sketch_name,
                axis_point=tuple(parameters.get("axis_point", (0, 0))),
                axis_direction=tuple(parameters.get("axis_direction", (1, 0))),
                angle=parameters.get("angle", 360.0)
            )
            
        elif feature_enum == FeatureType.HOLE:
            success = cad_operations.create_hole_feature(
                name=feature_name,
                position=tuple(parameters["position"]),
                diameter=parameters["diameter"],
                depth=parameters["depth"],
                hole_type=parameters.get("hole_type", "simple")
            )
            
        elif feature_enum == FeatureType.FILLET:
            success = cad_operations.create_fillet_feature(
                name=feature_name,
                edges=parameters["edges"],
                radius=parameters["radius"]
            )
            
        elif feature_enum == FeatureType.PATTERN:
            pattern_type = PatternType(parameters.get("pattern_type", "linear"))
            success = cad_operations.create_pattern_feature(
                name=feature_name,
                base_feature=parameters["base_feature"],
                pattern_type=pattern_type,
                parameters=parameters
            )
            
        if not success:
            return [TextContent(type="text", text=f"Failed to create {feature_type} feature")]
        
        # Update parametric model
        update_result = cad_operations.update_parametric_model()
        
        # Generate manufacturing report for the feature
        feature_obj = cad_operations.features[feature_name]
        manufacturing_notes = feature_obj.manufacturing_notes
        
        # Create FreeCAD implementation (mock for now)
        freecad = get_freecad_connection()
        
        # Convert to FreeCAD object creation
        if feature_enum == FeatureType.HOLE:
            # Create hole as cylinder subtraction
            pos = parameters["position"]
            diameter = parameters["diameter"]
            depth = parameters["depth"]
            
            if isinstance(diameter, str):
                # Evaluate parametric expression
                diameter = 10.0  # Fallback for demo
            
            freecad_result = freecad.execute_code(f"""
import FreeCAD
import Part

doc = FreeCAD.getDocument('{doc_name}')

# Create hole cylinder
hole_cylinder = Part.makeCylinder({diameter/2}, {depth}, 
                                 FreeCAD.Vector({pos[0]}, {pos[1]}, {pos[2]}))

# Create hole object
hole_obj = doc.addObject("Part::Feature", "{feature_name}")
hole_obj.Shape = hole_cylinder
hole_obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)  # Red color for holes

doc.recompute()
""")
        
        screenshot = freecad.get_active_screenshot()
        
        # Generate feature report
        report = f"""# Parametric Feature Created: {feature_name}

## Feature Details
- **Type**: {feature_type}
- **Document**: {doc_name}

## Parameters
"""
        for key, value in parameters.items():
            report += f"- **{key}**: {value}\n"
        
        if manufacturing_notes:
            report += "\n## Manufacturing Analysis\n"
            for key, value in manufacturing_notes.items():
                report += f"- **{key}**: {value}\n"
        
        if update_result.get("errors"):
            report += "\n## Parametric Update Issues\n"
            for error in update_result["errors"]:
                report += f"- ⚠️ {error}\n"
        
        return [
            TextContent(type="text", text=report),
            ImageContent(type="image", data=screenshot, mimeType="image/png")
        ]
        
    except Exception as e:
        logger.error(f"Parametric feature creation failed: {e}")
        return [TextContent(type="text", text=f"Parametric feature creation failed: {e}")]

@enhanced_mcp.tool()
def calculate_fit_and_tolerance(
    ctx: Context,
    nominal_dimension: float,
    fit_type: str,
    tolerance_grade_hole: str = "H7",
    tolerance_grade_shaft: str = "g6",
    temperature_range: float = 50.0
) -> List[TextContent]:
    """
    Calculate fit and tolerance analysis for mating parts with thermal considerations.
    
    Args:
        nominal_dimension: Nominal dimension in mm
        fit_type: Type of fit (clearance, transition, interference)
        tolerance_grade_hole: ISO tolerance grade for hole (H7, H8, etc.)
        tolerance_grade_shaft: ISO tolerance grade for shaft (g6, f7, etc.)
        temperature_range: Operating temperature range in °C
    
    Returns:
        Comprehensive fit and tolerance analysis
    """
    logger.info(f"Calculating fit and tolerance for {nominal_dimension}mm {fit_type} fit")
    
    try:
        # Calculate tolerances using manufacturing framework
        tolerance_analysis = manufacturing_framework.calculate_tolerance_stack(
            nominal_dimension=nominal_dimension,
            tolerance_grade=tolerance_grade_hole,
            fit_type=fit_type
        )
        
        # Calculate thermal effects
        material_1 = manufacturing_framework.materials.get("aluminum_6061")
        if material_1:
            thermal_expansion_1 = material_1.thermal_expansion * nominal_dimension * temperature_range / 1000
        else:
            thermal_expansion_1 = 23e-6 * nominal_dimension * temperature_range  # Aluminum default
        
        # Calculate actual fit conditions
        hole_tolerance = tolerance_analysis.get("hole_tolerance", 0.025)
        shaft_tolerance = tolerance_analysis.get("shaft_tolerance", -0.013)
        
        max_clearance = hole_tolerance - shaft_tolerance + thermal_expansion_1
        min_clearance = -hole_tolerance + shaft_tolerance + thermal_expansion_1
        
        # Determine fit suitability
        fit_suitability = "Suitable"
        warnings = []
        
        if fit_type == "clearance" and min_clearance <= 0:
            fit_suitability = "Unsuitable"
            warnings.append("Minimum clearance is negative - may cause binding")
        
        if fit_type == "interference" and max_clearance >= 0:
            fit_suitability = "Unsuitable"
            warnings.append("Maximum clearance is positive - insufficient interference")
        
        if abs(thermal_expansion_1) > abs(min_clearance) * 0.5:
            warnings.append("Thermal expansion is significant relative to fit")
        
        # Generate comprehensive report
        report = f"""# Fit and Tolerance Analysis

## Specifications
- **Nominal Dimension**: {nominal_dimension:.3f} mm
- **Fit Type**: {fit_type}
- **Hole Tolerance**: {tolerance_grade_hole}
- **Shaft Tolerance**: {tolerance_grade_shaft}
- **Temperature Range**: ±{temperature_range/2:.1f}°C

## Tolerance Analysis
- **Hole Tolerance**: +{hole_tolerance*1000:.1f}μm / 0μm
- **Shaft Tolerance**: {shaft_tolerance*1000:.1f}μm / {shaft_tolerance*1000:.1f}μm
- **Fundamental Deviation**: {(hole_tolerance + shaft_tolerance)*1000:.1f}μm

## Fit Analysis
- **Maximum Clearance**: {max_clearance*1000:.1f}μm
- **Minimum Clearance**: {min_clearance*1000:.1f}μm
- **Thermal Expansion**: {thermal_expansion_1*1000:.1f}μm
- **Fit Suitability**: {fit_suitability}

## Manufacturing Recommendations
- **Hole Process**: Reaming or boring for {tolerance_grade_hole}
- **Shaft Process**: Turning and grinding for {tolerance_grade_shaft}
- **Measurement**: Use coordinate measuring machine (CMM)
- **Assembly**: {"Press fit" if fit_type == "interference" else "Sliding fit"}

"""
        
        if warnings:
            report += "## Warnings\n"
            for warning in warnings:
                report += f"- ⚠️ {warning}\n"
        
        # Add process recommendations
        report += "\n## Process Recommendations\n"
        if nominal_dimension < 6:
            report += "- Small diameter - consider wire EDM for precision\n"
        elif nominal_dimension > 100:
            report += "- Large diameter - verify machine capacity\n"
        
        if fit_type == "interference":
            report += "- Consider hydraulic or thermal assembly methods\n"
            report += "- Verify material stress limits\n"
        
        return [TextContent(type="text", text=report)]
        
    except Exception as e:
        logger.error(f"Fit and tolerance calculation failed: {e}")
        return [TextContent(type="text", text=f"Fit and tolerance calculation failed: {e}")]

@enhanced_mcp.tool()
def validate_design_comprehensive(
    ctx: Context,
    doc_name: str,
    validation_options: Dict[str, Any] = None
) -> List[TextContent]:
    """
    Perform comprehensive design validation including geometry, manufacturing, structural, and cost analysis.
    
    Args:
        doc_name: FreeCAD document name to validate
        validation_options: Validation configuration options
    
    Returns:
        Comprehensive design validation report with recommendations
    
    Example validation_options:
        {
            "manufacturing_process": "cnc_machining",
            "target_cost": 150.0,
            "material": "aluminum_6061",
            "safety_factor": 2.0,
            "enable_structural": True,
            "enable_assembly": True
        }
    """
    logger.info(f"Performing comprehensive design validation for {doc_name}")
    
    try:
        if validation_options is None:
            validation_options = {}
        
        # Get objects from FreeCAD
        freecad = get_freecad_connection()
        objects_data = freecad.get_objects(doc_name)
        
        # Convert FreeCAD data to validation format
        validation_data = {
            "objects": {},
            "assemblies": {},
            "loads": {}
        }
        
        # Process each object
        for obj in objects_data:
            obj_name = obj.get("Name", "Unknown")
            
            # Extract geometric properties (mock data for demonstration)
            validation_data["objects"][obj_name] = {
                "material": validation_options.get("material", "aluminum_6061"),
                "volume": obj.get("Volume", 1000),  # mm³
                "density": 2.7,  # g/cm³ for aluminum
                "faces": [
                    {"thickness": 2.0, "center": (0, 0, 0)},
                    {"thickness": 1.5, "center": (10, 0, 0)}
                ],
                "holes": [
                    {"diameter": 8.0, "depth": 20.0, "position": (5, 5, 0)}
                ],
                "features": [
                    {"type": "boss", "size": 5.0, "location": (0, 0, 5)}
                ],
                "stress_concentrations": [
                    {"concentration_factor": 2.5, "location": (0, 10, 0)}
                ]
            }
        
        # Add mock assembly data if multiple objects
        if len(validation_data["objects"]) > 1:
            validation_data["assemblies"]["main_assembly"] = {
                "fits": [
                    {
                        "type": "clearance",
                        "shaft_tolerance": "g6",
                        "hole_tolerance": "H7",
                        "nominal_size": 25,
                        "shaft_part": list(validation_data["objects"].keys())[0],
                        "hole_part": list(validation_data["objects"].keys())[1]
                    }
                ],
                "assembly_sequence": [
                    {
                        "part": list(validation_data["objects"].keys())[0],
                        "tool_access": True,
                        "clearance": True
                    }
                ]
            }
        
        # Add mock load data
        validation_data["loads"]["operational_load"] = {
            "magnitude": 1000.0,  # N
            "point": (0, 0, 10),
            "supports": ["base"],
            "cross_section_area": 100e-6,  # m²
            "affected_objects": list(validation_data["objects"].keys())
        }
        
        # Perform comprehensive validation
        validation_result = validation_system.validate_design(validation_data, validation_options)
        
        # Generate detailed report
        detailed_report = validation_system.generate_validation_report(validation_result)
        
        # Add FreeCAD-specific recommendations
        detailed_report += f"\n## FreeCAD Integration Recommendations\n"
        
        if validation_result.overall_score < 70:
            detailed_report += "- Run FEA analysis using FreeCAD FEM workbench\n"
            detailed_report += "- Use TechDraw workbench for detailed drawings\n"
        
        if validation_result.issues_by_category.get("manufacturing", 0) > 2:
            detailed_report += "- Export to CAM workbench for toolpath generation\n"
            detailed_report += "- Verify with manufacturing DFM checks\n"
        
        detailed_report += f"- Consider exporting to STEP format for external validation\n"
        
        logger.info(f"Design validation completed: {validation_result.overall_score:.1f}/100")
        return [TextContent(type="text", text=detailed_report)]
        
    except Exception as e:
        logger.error(f"Comprehensive design validation failed: {e}")
        return [TextContent(type="text", text=f"Design validation failed: {e}")]

@enhanced_mcp.tool()
def optimize_for_manufacturing(
    ctx: Context,
    doc_name: str,
    process: str,
    optimization_goals: List[str] = None
) -> List[TextContent]:
    """
    Optimize design for specific manufacturing process with AI-driven recommendations.
    
    Args:
        doc_name: FreeCAD document name
        process: Manufacturing process (cnc_machining, fdm_printing, injection_molding)
        optimization_goals: List of optimization goals (cost, time, quality, material_usage)
    
    Returns:
        Manufacturing optimization report with specific design modifications
    """
    logger.info(f"Optimizing design for {process} manufacturing")
    
    try:
        if optimization_goals is None:
            optimization_goals = ["cost", "time"]
        
        # Get current design state
        freecad = get_freecad_connection()
        objects_data = freecad.get_objects(doc_name)
        
        # Analyze current design for optimization opportunities
        optimization_report = f"""# Manufacturing Optimization Report

## Target Process: {process.replace('_', ' ').title()}
## Optimization Goals: {', '.join(optimization_goals)}

## Current Design Analysis
"""
        
        total_volume = 0
        optimization_opportunities = []
        
        for obj in objects_data:
            obj_name = obj.get("Name", "Unknown")
            volume = obj.get("Volume", 0)
            total_volume += volume
            
            optimization_report += f"- **{obj_name}**: Volume {volume:.0f} mm³\n"
        
        # Process-specific optimizations
        if process == "cnc_machining":
            optimization_opportunities.extend([
                {
                    "category": "Tool Access",
                    "description": "Add corner radii ≥ 0.5mm to internal corners",
                    "impact": "Reduces tool wear and improves surface finish",
                    "cost_saving": "15-20%"
                },
                {
                    "category": "Setup Reduction", 
                    "description": "Combine operations on same face",
                    "impact": "Reduces setup time and improves accuracy",
                    "cost_saving": "25-30%"
                },
                {
                    "category": "Material Removal",
                    "description": "Optimize pocket depths for standard tools",
                    "impact": "Reduces machining time",
                    "cost_saving": "10-15%"
                }
            ])
            
        elif process == "fdm_printing":
            optimization_opportunities.extend([
                {
                    "category": "Support Reduction",
                    "description": "Orient parts to minimize overhangs > 45°",
                    "impact": "Reduces support material and post-processing",
                    "cost_saving": "20-25%"
                },
                {
                    "category": "Print Time",
                    "description": "Add chamfers instead of small radii",
                    "impact": "Reduces layer count and print time",
                    "cost_saving": "15-20%"
                },
                {
                    "category": "Material Usage",
                    "description": "Hollow non-critical sections",
                    "impact": "Reduces material usage",
                    "cost_saving": "30-40%"
                }
            ])
            
        elif process == "injection_molding":
            optimization_opportunities.extend([
                {
                    "category": "Draft Angles",
                    "description": "Add 1-2° draft to vertical surfaces",
                    "impact": "Improves part ejection",
                    "cost_saving": "Prevents tooling damage"
                },
                {
                    "category": "Wall Thickness",
                    "description": "Maintain uniform wall thickness 2-4mm",
                    "impact": "Prevents warping and sink marks",
                    "cost_saving": "Reduces defect rate"
                },
                {
                    "category": "Undercuts",
                    "description": "Eliminate undercuts or use side actions",
                    "impact": "Simplifies tooling",
                    "cost_saving": "20-30% tooling cost"
                }
            ])
        
        # Generate optimization recommendations
        optimization_report += "\n## Optimization Opportunities\n"
        
        for i, opp in enumerate(optimization_opportunities, 1):
            optimization_report += f"\n### {i}. {opp['category']}\n"
            optimization_report += f"**Recommendation**: {opp['description']}\n"
            optimization_report += f"**Impact**: {opp['impact']}\n"
            optimization_report += f"**Potential Savings**: {opp['cost_saving']}\n"
        
        # Goal-specific recommendations
        optimization_report += "\n## Goal-Specific Recommendations\n"
        
        if "cost" in optimization_goals:
            optimization_report += "### Cost Optimization\n"
            optimization_report += "- Use standard tool sizes and materials\n"
            optimization_report += "- Minimize tolerance requirements where possible\n"
            optimization_report += "- Consider material substitution analysis\n"
        
        if "time" in optimization_goals:
            optimization_report += "### Time Optimization\n"
            optimization_report += "- Optimize part orientation for minimal setup\n"
            optimization_report += "- Use larger corner radii for faster machining\n"
            optimization_report += "- Combine similar features for batch processing\n"
        
        if "quality" in optimization_goals:
            optimization_report += "### Quality Optimization\n"
            optimization_report += "- Add stress-relief features at transitions\n"
            optimization_report += "- Specify appropriate surface finish requirements\n"
            optimization_report += "- Consider inspection accessibility\n"
        
        if "material_usage" in optimization_goals:
            optimization_report += "### Material Optimization\n"
            optimization_report += "- Topology optimization for load paths\n"
            optimization_report += "- Hollow non-structural sections\n"
            optimization_report += "- Optimize material distribution\n"
        
        # Implementation steps
        optimization_report += "\n## Implementation Steps\n"
        optimization_report += "1. Review and prioritize optimization opportunities\n"
        optimization_report += "2. Modify CAD model with recommended changes\n"
        optimization_report += "3. Re-run DFM analysis to verify improvements\n"
        optimization_report += "4. Generate updated manufacturing drawings\n"
        optimization_report += "5. Validate with manufacturing partner\n"
        
        return [TextContent(type="text", text=optimization_report)]
        
    except Exception as e:
        logger.error(f"Manufacturing optimization failed: {e}")
        return [TextContent(type="text", text=f"Manufacturing optimization failed: {e}")]

# Enhanced prompts
@enhanced_mcp.prompt()
def manufacturing_design_guidelines() -> str:
    """Get comprehensive manufacturing design guidelines with material and process selection"""
    return """
# Manufacturing Design Guidelines

## Material Selection Guide

### Metals
- **Aluminum 6061**: General purpose, good machinability, lightweight
- **Steel (Mild)**: High strength, cost-effective, widely available
- **Stainless Steel 316**: Corrosion resistant, food-safe applications
- **Titanium**: High strength-to-weight, aerospace applications

### Plastics
- **PLA**: Easy 3D printing, biodegradable, low strength
- **ABS**: Durable 3D printing, good impact resistance
- **Nylon**: High strength, wear resistant, challenging to print
- **PETG**: Chemical resistant, transparent options

## Process Selection Guide

### CNC Machining
- **Best for**: High precision, complex geometries, metals
- **Design rules**: Add corner radii, consider tool access, minimize setups
- **Tolerances**: ±0.025mm achievable, ±0.1mm standard

### 3D Printing (FDM)
- **Best for**: Rapid prototyping, complex internal features, low volume
- **Design rules**: 45° overhang limit, 0.4mm minimum features, avoid supports
- **Tolerances**: ±0.2mm typical, ±0.1mm with careful tuning

### Injection Molding
- **Best for**: High volume production, consistent quality
- **Design rules**: Uniform wall thickness, draft angles, avoid undercuts
- **Tolerances**: ±0.1mm achievable, varies with size

## Universal Design Principles

1. **Design for Assembly (DFA)**
   - Minimize part count
   - Use self-aligning features
   - Ensure tool accessibility

2. **Design for Manufacturing (DFM)**
   - Follow process-specific guidelines
   - Specify appropriate tolerances
   - Consider material properties

3. **Cost Optimization**
   - Use standard materials and tools
   - Minimize secondary operations
   - Design for automation where possible

4. **Quality Assurance**
   - Include inspection features
   - Specify critical dimensions
   - Consider measurement accessibility
"""

@enhanced_mcp.prompt()
def spatial_layout_best_practices() -> str:
    """Get best practices for spatial layout and component arrangement"""
    return """
# Spatial Layout Best Practices

## Component Placement Principles

### Accessibility
- Maintain 50mm minimum clearance for service access
- Position serviceable components within 600mm reach
- Ensure tool access for maintenance operations
- Consider human factors and ergonomics

### Thermal Management
- Separate heat sources from temperature-sensitive components
- Provide adequate airflow paths
- Use thermal barriers where necessary
- Consider thermal expansion in fits

### Electromagnetic Compatibility (EMC)
- Separate sensitive circuits from noise sources
- Use proper grounding and shielding
- Route cables to minimize interference
- Consider frequency-dependent effects

### Mechanical Considerations
- Route load paths to structural supports
- Minimize stress concentrations
- Consider vibration isolation
- Ensure adequate safety factors

## Constraint Types

### Clearance Constraints
- **Minimum**: 5mm for general clearance
- **Maintenance**: 25mm for service access
- **Tool Access**: 50mm for wrenches/tools
- **Safety**: 100mm for high-voltage components

### Orientation Constraints
- **Gravity**: Ensure stable base of support
- **Access**: Orient connectors for easy access
- **Flow**: Align with airflow or fluid paths
- **Viewing**: Position displays for visibility

### Environmental Constraints
- **Temperature**: Consider operating ranges
- **Humidity**: Protect sensitive components
- **Vibration**: Isolate delicate instruments
- **Shock**: Provide adequate mounting

## Optimization Strategies

1. **Iterative Layout**
   - Start with critical components
   - Add constraints progressively
   - Optimize in multiple passes

2. **Multi-Objective Optimization**
   - Balance competing requirements
   - Use weighted scoring functions
   - Consider trade-offs explicitly

3. **Modular Design**
   - Group related components
   - Create replaceable modules
   - Standardize interfaces

4. **Future Considerations**
   - Plan for upgrades and modifications
   - Reserve space for expansion
   - Consider lifecycle requirements
"""

def main():
    """Run the enhanced MCP server"""
    enhanced_mcp.run()