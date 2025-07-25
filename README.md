# Taiyaki AI - Enhanced FreeCAD Integration

Taiyaki AI is a comprehensive FreeCAD integration toolkit that leverages the Model Context Protocol (MCP) to enable advanced programmatic control of 3D modeling operations. This enhanced framework provides a powerful API for creating and manipulating 3D models in FreeCAD with advanced manufacturing analysis, spatial reasoning, and design validation capabilities.

## Features

### Core Integration
- **Advanced API Integration**: Connect FreeCAD to external systems using MCP
- **Parametric Modeling**: Create customizable geometric models with precise parameters
- **STEP Export**: Export to industry-standard CAD formats
- **Automated Server**: Auto-starting RPC server with connection testing
- **Enhanced User Interface**: Improved workbench experience in FreeCAD
- **Knowledge Base**: Integrated knowledge base with specialized CAD guidelines and best practices

### Enhanced Manufacturing Framework
- **Manufacturing Analysis**: Comprehensive material selection and process optimization
- **Tolerance Calculations**: Advanced fit and tolerance analysis with thermal considerations
- **Cost Estimation**: Intelligent cost analysis with process-specific parameters
- **DFM Integration**: Design for Manufacturing checks with actionable recommendations
- **Multi-Process Support**: CNC machining, 3D printing, injection molding, and more

### Spatial Reasoning & Layout
- **Physics-Based Constraints**: Collision detection and gravity-aware positioning
- **Ergonomic Analysis**: Human factors integration for accessible design
- **Thermal Management**: Heat dissipation and thermal expansion analysis
- **Assembly Optimization**: Constraint-based spatial layout optimization
- **Accessibility Validation**: Tool access and maintenance clearance verification

### Advanced CAD Operations
- **Feature-Based Modeling**: Parametric sketches with geometric constraints
- **Pattern Generation**: Linear, circular, and path-based pattern creation
- **Boolean Operations**: Advanced union, subtract, and intersect with manufacturing awareness
- **Assembly Management**: Multi-component assemblies with constraint validation
- **Parametric Expressions**: Variable-driven dimensions with dependency tracking

### Design Validation System
- **Comprehensive Analysis**: Geometry, manufacturing, structural, assembly, and cost validation
- **Severity Classification**: Critical, error, warning, and info level issue detection
- **Manufacturing Validation**: Process-specific design rule checking
- **Structural Analysis**: Stress concentration and load path validation
- **Cost Optimization**: Target cost validation with optimization recommendations

### Screenshot Analysis & Auto-Fix
- **Visual Analysis**: AI-powered screenshot analysis to detect geometric issues
- **Automatic Error Detection**: Identifies zero dimensions, overlapping objects, and manufacturing constraints
- **Auto-Fix Capabilities**: Automatically resolves common CAD design issues
- **Manufacturing Validation**: Ensures designs meet production requirements
- **Spatial Conflict Resolution**: Detects and fixes overlapping or conflicting geometry

### Web STEP File Import
- **Professional CAD Libraries**: Direct access to McMaster-Carr, GrabCAD, TraceParts, and manufacturer websites
- **Intelligent Search**: Web search integration for finding existing STEP files instead of modeling from scratch
- **Part Number Lookup**: Direct McMaster-Carr part import using standard part numbers
- **Quality Sources**: Focus on professional-grade, dimensionally accurate CAD models
- **Part Management**: Organize and categorize imported components automatically
- **Assembly Integration**: Seamlessly incorporate standard components into custom designs

## Installation 

See the [Installation Guide](INSTALLATION.md) for complete setup instructions.

## MCP Tools

The Taiyaki AI toolkit exposes the following API endpoints through MCP:

### Standard Tools
* `create_document`: Create a new document in FreeCAD
* `create_object`: Create a new object in FreeCAD
* `edit_object`: Edit an object in FreeCAD
* `delete_object`: Delete an object in FreeCAD
* `execute_code`: Execute arbitrary Python code in FreeCAD
* `insert_part_from_library`: Insert a part from the parts library
* `get_view`: Get a screenshot of the active view
* `get_objects`: Get all objects in a document
* `get_object`: Get an object in a document
* `get_parts_list`: Get the list of parts in the parts library

### Enhanced Manufacturing Tools
* `export_step`: Export models to industry-standard STEP format for manufacturing or sharing
* `analyze_manufacturing_requirements`: Comprehensive manufacturing analysis with cost estimates
* `calculate_fit_and_tolerance`: Advanced fit and tolerance analysis with thermal considerations
* `optimize_for_manufacturing`: AI-driven manufacturing optimization with process-specific recommendations
* `validate_design_comprehensive`: Complete design validation across all engineering domains

### Spatial Layout Tools
* `create_spatial_layout`: Physics-based spatial layout with collision detection and optimization
* Advanced constraint solving for clearance, accessibility, thermal, and ergonomic requirements
* Automated layout optimization with multi-objective scoring

### Advanced CAD Tools
* `create_parametric_feature`: Feature-based modeling with manufacturing integration
* Parametric sketches with geometric constraints and variable expressions
* Pattern generation (linear, circular, path-based) with manufacturing awareness
* Boolean operations with design validation

### Design Validation Tools
* Multi-domain validation (geometry, manufacturing, structural, assembly, cost)
* Severity-based issue classification and prioritization
* Actionable recommendations with cost and time impact analysis
* Process-specific design rule checking

### Screenshot Analysis & Auto-Fix Tools
* `analyze_screenshot_for_issues`: AI-powered visual analysis of FreeCAD screenshots to detect design issues
* `apply_automatic_fixes`: Automatically fix common geometric and manufacturing issues
* Visual error detection for zero dimensions, invalid parameters, and spatial conflicts
* Manufacturing constraint validation and automatic thickness adjustments
* Spatial layout optimization with automatic object separation

### Web STEP File Import Tools
* `search_and_import_step_files`: Search web sources for existing STEP files and import directly
* `import_mcmaster_part`: Import specific McMaster-Carr parts using part numbers
* `manage_imported_parts`: Organize and categorize imported components
* Professional CAD library integration (McMaster-Carr, GrabCAD, TraceParts)
* Intelligent part identification and organization by function
* Quality source prioritization for dimensionally accurate models

### Legacy DFM Tools
* `get_printing_guidelines`: Direct access to detailed 3D printing design guidelines
* `refine_3d_printing_dfm`: Refine a 3D printing design for specific processes (e.g., SLA, SLS) using DFM rules
* `refine_cnc_machining_dfm`: Refine a CNC machining design for specific processes using DFM rules
* `analyze_cnc_manufacturing_dfm`: Visual DFM analysis for CNC machining
* `analyze_3d_printing_dfm`: Visual DFM analysis for 3D printing
* `analyze_injection_molding_dfm`: Visual DFM analysis for injection molding  

## Knowledge Base System

Taiyaki AI includes a comprehensive knowledge base system that provides specialized domain knowledge to Claude Desktop through the MCP protocol. This knowledge base enhances Claude's understanding of CAD operations, manufacturing processes, and design best practices.

As for the guidelines, the knowledge base is designed to be modular and extensible. It can be easily updates with the new information just by repacing the corresponding CSV files in `prompts` folder.

Currently, for working with specific manufacturing processes (3D Printing or CNC Machining), we load the appropriate prompt, inside of which there are injected features and processes from knowledge base CSV files. Using this information, the AI assistant can accurately query the knowledge base tables with `refine_3d_printing_dfm` and `refine_cnc_machining_dfm` tools to refine the design for specific processes or answer user's questions about design rules and best practices.

### Available Prompts

The knowledge base includes the following specialized prompt modules:

1. **Asset Creation Strategy** (`asset_creation_strategy`)
   - Basic strategy for creating assets in FreeCAD
   - Guidelines for using parametric modeling vs. direct modeling
   - Best practices for object creation, naming, and organization

2. **3D Printing & CNC Machining Guidelines** (`printing_guidelines`)
   - Detailed design rules for various 3D printing processes (DMLS, SLA, SLS, MJF, etc.)  
   - Detailed design rules for CNC machining  
   - Process-specific parameters including layer thickness, minimum feature sizes, tolerances
   - Best practices for designing printable models
   - Practical FreeCAD examples with code snippets

3. **Boolean Operations Guide** (`boolean_operations`)
   - Comprehensive guide for using union, difference, and intersection operations
   - Best practices for creating complex shapes through boolean operations
   - Troubleshooting common boolean operation issues
   - Practical examples with code snippets

4. **Feature Modeling Guide** (`feature_modeling`)
   - Techniques for creating features like fillets, chamfers, and shells
   - Best practices for feature-based modeling
   - Examples with code snippets

5. **Pattern Generation Guide** (`pattern_generation`)
   - Methods for creating rectangular arrays, polar arrays, and mirrors
   - Best practices for pattern generation
   - Examples with code snippets

### Accessing Knowledge

The knowledge base can be accessed through two methods:

1. **Implicit Prompts**: Claude will automatically use the knowledge when you ask questions about related topics.

2. **Direct Tool Access**: For specific knowledge domains, you can use dedicated tools:
   - `get_printing_guidelines`: Directly access the 3D printing design guidelines
   - More direct access tools will be added in future releases

## Usage Examples

### Enhanced Manufacturing Analysis

```python
# Comprehensive manufacturing analysis
analyze_manufacturing_requirements(
  doc_name="MyPart",
  material="aluminum_6061",
  process="cnc_milling",
  tolerance_grade="IT7",
  surface_finish=1.6
)

# Advanced fit and tolerance calculation
calculate_fit_and_tolerance(
  nominal_dimension=25.0,
  fit_type="clearance",
  tolerance_grade_hole="H7",
  tolerance_grade_shaft="g6",
  temperature_range=50.0
)
```

### Spatial Layout and Optimization

```python
# Create optimized spatial layout
create_spatial_layout(
  layout_name="motor_assembly",
  components=[
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
  ],
  constraints=[
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
)
```

### Advanced Parametric Features

```python
# Create parametric hole with manufacturing integration
create_parametric_feature(
  doc_name="MyPart",
  feature_name="mounting_hole",
  feature_type="hole",
  parameters={
    "position": [10, 20, 0],
    "diameter": "bolt_diameter * 1.1",  # Parametric expression
    "depth": 15.0,
    "hole_type": "precision"
  }
)

# Create fillet with manufacturing considerations
create_parametric_feature(
  doc_name="MyPart",
  feature_name="stress_relief",
  feature_type="fillet",
  parameters={
    "edges": ["Box.Edge1", "Box.Edge2"],
    "radius": "wall_thickness * 0.5"
  }
)
```

### Comprehensive Design Validation

```python
# Complete design validation
validate_design_comprehensive(
  doc_name="MyAssembly",
  validation_options={
    "manufacturing_process": "cnc_machining",
    "target_cost": 150.0,
    "material": "aluminum_6061",
    "safety_factor": 2.0,
    "enable_structural": True,
    "enable_assembly": True
  }
)

# Manufacturing optimization
optimize_for_manufacturing(
  doc_name="MyPart",
  process="cnc_machining",
  optimization_goals=["cost", "time", "quality"]
)
```

### Web STEP File Import

```python
# Search and import standard fasteners
search_and_import_step_files(
  doc_name="MyAssembly",
  search_query="M8 hex bolt",
  preferred_sources=["mcmaster", "grabcad"],
  max_results=3
)

# Import specific McMaster-Carr parts
import_mcmaster_part(
  doc_name="FastenerLibrary",
  part_number="91290A115",  # M8x25mm hex bolt
  description="Standard hex bolt"
)

# Search for bearings from professional sources
search_and_import_step_files(
  doc_name="BearingAssembly",
  search_query="608 ball bearing",
  preferred_sources=["mcmaster", "manufacturer"]
)

# Organize imported parts
manage_imported_parts(
  doc_name="MyAssembly",
  action="organize"  # Groups by fasteners, bearings, etc.
)

# List all imported components
manage_imported_parts(
  doc_name="MyAssembly",
  action="list"
)
```

### Legacy Examples

```python
# Create a Parametric Box (legacy)
create_parametric_model(
  doc_name="MyModel",
  model_type="box",
  parameters={
    "length": 20,
    "width": 15, 
    "height": 10,
    "color": [1.0, 0.0, 0.0, 1.0],
    "position": {"x": 0, "y": 0, "z": 0}
  }
)

# Export a Model to STEP
export_step(
  doc_name="MyModel",
  file_name="my_exported_model.step",
  export_to="desktop"
)

# Get Guidelines (legacy)
guidelines_3d_prompt = get_3d_printing_guidelines_prompt()
guidelines_cnc_prompt = get_cnc_machining_guidelines_prompt()

# Get specific DFM information
result = refine_3d_printing_dfm(
   features=["Layer Thickness"],
   processes=["SLA"]
)

result = refine_cnc_machining_dfm(
   features=["Standard Tolerance"]
)
```

## Enhanced Architecture

The enhanced Taiyaki AI system is built on four core frameworks that work together to provide comprehensive CAD and manufacturing capabilities:

### Manufacturing Framework (`manufacturing_framework.py`)
- **Material Database**: Comprehensive material properties including mechanical, thermal, and cost data
- **Process Library**: Manufacturing process definitions with constraints and capabilities
- **Tolerance Engine**: ISO-standard tolerance calculations with fit analysis
- **Cost Estimation**: Process-specific cost modeling with time and material factors
- **DFM Integration**: Design for Manufacturing rule checking and optimization

### Spatial Framework (`enhanced_spatial_framework.py`)
- **Physics-Based Layout**: Collision detection with bounding box optimization
- **Constraint Solver**: Multi-objective constraint satisfaction for spatial relationships
- **Ergonomic Analysis**: Human factors integration for accessibility and usability
- **Thermal Management**: Heat dissipation modeling and thermal expansion analysis
- **Assembly Optimization**: Automated layout optimization with configurable priorities

### CAD Operations Framework (`advanced_cad_operations.py`)
- **Parametric Modeling**: Variable-driven features with dependency tracking
- **Sketch Engine**: Geometric constraint solving for 2D sketches
- **Feature Library**: Extrude, revolve, fillet, pattern, and boolean operations
- **Assembly Management**: Multi-component assemblies with constraint validation
- **Manufacturing Integration**: Feature-level DFM analysis and recommendations

### Design Validation System (`design_validation_system.py`)
- **Multi-Domain Validation**: Geometry, manufacturing, structural, assembly, and cost analysis
- **Severity Classification**: Critical, error, warning, and info level issue categorization
- **Rule Engine**: Extensible validation rules with configurable parameters
- **Impact Analysis**: Cost and time impact estimation for identified issues
- **Recommendation Engine**: Actionable improvement suggestions with priority ranking

## Server Architecture

The system provides two server implementations:

1. **Standard Server** (`server.py`): Original FreeCAD MCP integration with DFM capabilities
2. **Enhanced Server** (`enhanced_server.py`): Advanced server with all four frameworks integrated

Both servers maintain backward compatibility while the enhanced server provides additional advanced capabilities.

## Configuration

Configure the appropriate MCP client to connect to the Taiyaki AI server. The server exposes a standard MCP interface at port 8000 by default.

### Enhanced Server Configuration

To use the enhanced capabilities, ensure your MCP client points to the enhanced server:

```json
{
  "mcpServers": {
    "taiyaki-ai-enhanced": {
      "command": "python",
      "args": ["-m", "freecad_mcp.enhanced_server"],
      "env": {
        "FREECAD_PATH": "/path/to/freecad"
      }
    }
  }
}
```

### Framework Initialization

The enhanced server automatically initializes all frameworks with standard materials and processes:

- **Materials**: Aluminum 6061, Steel (mild), PLA, ABS
- **Processes**: CNC milling, FDM printing, injection molding
- **Tolerances**: ISO standard grades (IT6-IT12)
- **Validation Rules**: Comprehensive rule set for all categories