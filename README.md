# Taiyaki AI - FreeCAD Integration

Taiyaki AI is a comprehensive FreeCAD integration toolkit that leverages the Model Context Protocol (MCP) to enable advanced programmatic control of 3D modeling operations. This framework provides a powerful API for creating and manipulating 3D models in FreeCAD through structured commands.

## Features

- **Advanced API Integration**: Connect FreeCAD to external systems using MCP
- **Parametric Modeling**: Create customizable geometric models with precise parameters
- **STEP Export**: Export to industry-standard CAD formats
- **Automated Server**: Auto-starting RPC server with connection testing
- **Enhanced User Interface**: Improved workbench experience in FreeCAD
- **Knowledge Base**: Integrated knowledge base with specialized CAD guidelines and best practices

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

### Enhanced Tools
* `export_step`: Export models to industry-standard STEP format for manufacturing or sharing;    
* `get_printing_guidelines`: Direct access to detailed 3D printing design guidelines;  
* `refine_3d_printing_dfm`: Refine a 3D printing design for specific processes (e.g., SLA, SLS) using DFM rules;  
* `refine_cnc_machining_dfm`: Refine a CNC machining design for specific processes using DFM rules.  

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

### Create a Parametric Box

```python
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
```

### Export a Model to STEP

```python
export_step(
  doc_name="MyModel",
  file_name="my_exported_model.step",
  export_to="desktop"
)
```

### Get Gudelines

```python
# Get all 3D printing guidelines
guidelines_3d_prompt = get_3d_printing_guidelines_prompt()
gudelines_cnc_prompt = get_cnc_machining_guidelines_prompt()

# Get specific DFM information
result = refine_3d_printing_dfm(
   features=["Layer Thickness"],
   processes=["SLA"]
)

result = refine_cnc_machining_dfm(
   features=["Standard Tolerance"]
)

```

## Configuration

Configure the appropriate MCP client to connect to the Taiyaki AI server. The server exposes a standard MCP interface at port 8000 by default.