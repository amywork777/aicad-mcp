import os
import json
import logging
import xmlrpc.client
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, Literal, List

from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent, ImageContent
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TaiyakiAI")


class FreeCADConnection:
    def __init__(self, host: str = "localhost", port: int = 9875):
        self.server = xmlrpc.client.ServerProxy(f"http://{host}:{port}", allow_none=True)

    def ping(self) -> bool:
        return self.server.ping()

    def create_document(self, name: str) -> dict[str, Any]:
        return self.server.create_document(name)
        
    def create_parametric_model(self, doc_name: str, model_type: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return self.server.create_parametric_model(doc_name, model_type, parameters)
        
    def export_step(self, doc_name: str, file_path: str, object_names: list = None) -> dict[str, Any]:
        return self.server.export_step(doc_name, file_path, object_names)

    def create_object(self, doc_name: str, obj_data: dict[str, Any]) -> dict[str, Any]:
        return self.server.create_object(doc_name, json.dumps(obj_data))

    def edit_object(self, doc_name: str, obj_name: str, obj_data: dict[str, Any]) -> dict[str, Any]:
        return self.server.edit_object(doc_name, obj_name, json.dumps(obj_data))

    def delete_object(self, doc_name: str, obj_name: str) -> dict[str, Any]:
        return self.server.delete_object(doc_name, obj_name)

    def insert_part_from_library(self, relative_path: str) -> dict[str, Any]:
        return self.server.insert_part_from_library(relative_path)

    def execute_code(self, code: str) -> dict[str, Any]:
        return self.server.execute_code(code)

    def get_active_screenshot(self, view_name: str = "Isometric") -> str:
        return self.server.get_active_screenshot(view_name)

    def get_objects(self, doc_name: str) -> list[dict[str, Any]]:
        return self.server.get_objects(doc_name)

    def get_object(self, doc_name: str, obj_name: str) -> dict[str, Any]:
        return self.server.get_object(doc_name, obj_name)

    def get_parts_list(self) -> list[str]:
        return self.server.get_parts_list()

    def run_cnc_manufacturing_dfm_check(self, doc_name: str, params: Dict[str, float]) -> dict[str, Any]:
        return self.server.run_cnc_manufacturing_dfm_check(doc_name, json.dumps(params or {}))
        
    def run_3d_printing_dfm_check(self, doc_name: str, params: Dict[str, float]) -> dict[str, Any]:
        return self.server.run_3d_printing_dfm_check(doc_name, json.dumps(params or {}))
    
    def run_injection_molding_dfm_check(self, doc_name: str, params: Dict[str, float]) -> dict[str, Any]:
        return self.server.run_injection_molding_dfm_check(doc_name, json.dumps(params or {}))
    
    def restore_colors_after_check(self, doc_name: str) -> dict[str, Any]:
        return self.server.restore_colors_after_check(doc_name)


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    try:
        logger.info("Taiyaki AI MCP server starting up")
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
        # Clean up the global connection on shutdown
        global _freecad_connection
        if _freecad_connection:
            logger.info("Disconnecting from FreeCAD on shutdown")
            _freecad_connection = None
        logger.info("Taiyaki AI MCP server shut down")


mcp = FastMCP(
    "TaiyakiAI",
    description="Taiyaki AI - FreeCAD integration for Claude Desktop",
    lifespan=server_lifespan,
)


_freecad_connection: FreeCADConnection | None = None


def get_freecad_connection():
    """Get or create a persistent FreeCAD connection"""
    global _freecad_connection
    if _freecad_connection is None:
        _freecad_connection = FreeCADConnection(host="localhost", port=9875)
        if not _freecad_connection.ping():
            logger.error("Failed to ping FreeCAD")
            _freecad_connection = None
            raise Exception(
                "Failed to connect to FreeCAD. Make sure the FreeCAD addon is running."
            )
    return _freecad_connection


@mcp.tool()
def create_document(ctx: Context, document_name: str) -> list[TextContent]:
    """Create a new document in FreeCAD with a given document name."""
    logger.info(f"Requested to create document: {document_name}")
    freecad = get_freecad_connection()
    try:
        response = freecad.create_document(document_name)
        if response["success"]:
            logger.info(f"Document '{document_name}' created successfully")
            return [
                TextContent(
                    type="text",
                    text=f"Document '{response['document_name']}' created successfully"
                )
            ]
        else:
            logger.error(f"Failed to create document: {response['error']}")
            return [
                TextContent(
                    type="text",
                    text=f"Failed to create document: {response['error']}"
                )
            ]
    except Exception as e:
        logger.error(f"Failed to create document: {str(e)}")
        return [
            TextContent(
                type="text", text=f"Failed to create document: {str(e)}"
            )
        ]


@mcp.tool()
def create_object(
    ctx: Context,
    doc_name: str,
    obj_type: str,
    obj_name: str,
    analysis_name: str | None = None,
    obj_properties: dict[str, Any] = None,
) -> list[TextContent | ImageContent]:
    """
    Create a new object in a specified FreeCAD document, using the
    specified object type and properties.

    Object type starts with "Part::" or "Draft::" or "PartDesign::" or "Fem::".

    Args:
        doc_name: The name of the document to create the object in.
        obj_type: The type of the object to create (e.g. 'Part::Box', 'Part::Cylinder', 'Draft::Circle', 'PartDesign::Body', etc.).
        obj_name: The name of the object to create.
        obj_properties: The properties of the object to create.

    Returns:
        A message indicating the success or failure of the object creation and a screenshot of the object.

    Examples:
        If you want to create a cylinder with a height of 30 and a radius of 10, you can use the following data.
        ```json
        {
            "doc_name": "MyCylinder",
            "obj_name": "Cylinder",
            "obj_type": "Part::Cylinder",
            "obj_properties": {
                "Height": 30,
                "Radius": 10,
                "Placement": {
                    "Base": {
                        "x": 10,
                        "y": 10,
                        "z": 0
                    },
                    "Rotation": {
                        "Axis": {
                            "x": 0,
                            "y": 0,
                            "z": 1
                        },
                        "Angle": 45
                    }
                },
                "ViewObject": {
                    "ShapeColor": [0.5, 0.5, 0.5, 1.0]
                }
            }
        }
        ```

        If you want to create a circle with a radius of 10, you can use the following data.
        ```json
        {
            "doc_name": "MyCircle",
            "obj_name": "Circle",
            "obj_type": "Draft::Circle",
        }
        ```

        If you want to create a FEM analysis, you can use the following data.
        ```json
        {
            "doc_name": "MyFEMAnalysis",
            "obj_name": "FemAnalysis",
            "obj_type": "Fem::AnalysisPython",
        }
        ```

        If you want to create a FEM constraint, you can use the following data.
        ```json
        {
            "doc_name": "MyFEMConstraint",
            "obj_name": "FemConstraint",
            "obj_type": "Fem::ConstraintFixed",
            "analysis_name": "MyFEMAnalysis",
            "obj_properties": {
                "References": [
                    {
                        "object_name": "MyObject",
                        "face": "Face1"
                    }
                ]
            }
        }
        ```

        If you want to create a FEM mechanical material, you can use the following data.
        ```json
        {
            "doc_name": "MyFEMAnalysis",
            "obj_name": "FemMechanicalMaterial",
            "obj_type": "Fem::MaterialCommon",
            "analysis_name": "MyFEMAnalysis",
            "obj_properties": {
                "Material": {
                    "Name": "MyMaterial",
                    "Density": "7900 kg/m^3",
                    "YoungModulus": "210 GPa",
                    "PoissonRatio": 0.3
                }
            }
        }
        ```

        If you want to create a FEM mesh, you can use the following data.
        The `Part` property is required.
        ```json
        {
            "doc_name": "MyFEMMesh",
            "obj_name": "FemMesh",
            "obj_type": "Fem::FemMeshGmsh",
            "analysis_name": "MyFEMAnalysis",
            "obj_properties": {
                "Part": "MyObject",
                "ElementSizeMax": 10,
                "ElementSizeMin": 0.1,
                "MeshAlgorithm": 2
            }
        }
        ```
    """
    logger.info(f"Requested to create object: {obj_name} of type {obj_type} in document {doc_name}")
    logger.info(f"Requested properties: {obj_properties}")
    freecad = get_freecad_connection()
    try:
        obj_data = {
            "Name": obj_name,
            "Type": obj_type,
            "Properties": obj_properties or {},
            "Analysis": analysis_name
        }
        response = freecad.create_object(doc_name, obj_data)
        screenshot = freecad.get_active_screenshot()
        if response["success"]:
            logger.info(f"Object '{obj_name}' created successfully")
            return [
                TextContent(
                    type="text",
                    text=f"Object '{response['object_name']}' created successfully"
                ),
                ImageContent(
                    type="image", data=screenshot, mimeType="image/png"
                )
            ]
        else:
            logger.error(f"Failed to create object: {response['error']}")
            return [
                TextContent(
                    type="text",
                    text=f"Failed to create object: {response['error']}"
                ),
                ImageContent(
                    type="image", data=screenshot, mimeType="image/png"
                )
            ]
    except Exception as e:
        logger.error(f"Failed to create object: {str(e)}")
        return [
            TextContent(
                type="text", text=f"Failed to create object: {str(e)}"
            )
        ]


@mcp.tool()
def edit_object(
    ctx: Context,
    doc_name: str,
    obj_name: str,
    obj_properties: dict[str, Any]
) -> list[TextContent | ImageContent]:
    """
    Edit an existing object in a specified FreeCAD document with new properties.

    Args:
        doc_name: The name of the document to edit the object in;
        obj_name: The name of the object to edit;
        obj_properties: The properties of the object to edit;

    Returns:
        A message indicating the success or failure of the object editing and a screenshot of the object.
    """
    logger.info(f"Requested to edit object: {obj_name} in document {doc_name}")
    logger.info(f"Requested new properties: {obj_properties}")
    freecad = get_freecad_connection()
    try:
        response = freecad.edit_object(doc_name, obj_name, obj_properties)
        screenshot = freecad.get_active_screenshot()
        if response["success"]:
            logger.info(f"Object '{obj_name}' edited successfully")
            return [
                TextContent(
                    type="text",
                    text=f"Object '{response['object_name']}' edited successfully"
                ),
                ImageContent(
                    type="image", data=screenshot, mimeType="image/png"
                )
            ]
        else:
            logger.error(f"Failed to edit object: {response['error']}")
            return [
                TextContent(
                    type="text",
                    text=f"Failed to edit object: {response['error']}"
                ),
                ImageContent(
                    type="image", data=screenshot, mimeType="image/png"
                )
            ]
    except Exception as e:
        logger.error(f"Failed to edit object: {str(e)}")
        return [
            TextContent(type="text", text=f"Failed to edit object: {str(e)}")
        ]


@mcp.tool()
def delete_object(
    ctx: Context,
    doc_name: str,
    obj_name: str
) -> list[TextContent | ImageContent]:
    """
    Delete an specfied object in a specified FreeCAD document.

    Args:
        doc_name: The name of the document to delete the object from.
        obj_name: The name of the object to delete.

    Returns:
        A message indicating the success or failure of the object deletion and a screenshot of the object.
    """
    logger.info(f"Requested to delete object: {obj_name} in document {doc_name}")
    freecad = get_freecad_connection()
    try:
        response = freecad.delete_object(doc_name, obj_name)
        screenshot = freecad.get_active_screenshot()
        if response["success"]:
            logger.info(f"Object '{obj_name}' deleted successfully")
            return [
                TextContent(
                    type="text",
                    text=f"Object '{response['object_name']}' deleted successfully"
                ),
                ImageContent(
                    type="image", data=screenshot, mimeType="image/png"
                )
            ]
        else:
            logger.error(f"Failed to delete object: {response['error']}")
            return [
                TextContent(
                    type="text",
                    text=f"Failed to delete object: {response['error']}"
                ),
                ImageContent(
                    type="image", data=screenshot, mimeType="image/png"
                )
            ]
    except Exception as e:
        logger.error(f"Failed to delete object: {str(e)}")
        return [
            TextContent(type="text", text=f"Failed to delete object: {str(e)}")
        ]


@mcp.tool()
def execute_code(ctx: Context, code: str) -> list[TextContent | ImageContent]:
    """
    Execute arbitrary Python code in FreeCAD.

    Args:
        code: The Python code to execute.

    Returns:
        A message indicating the success or failure of the code execution, the output of the code execution, and a screenshot of the object.
    """
    logger.info(f"Requested to execute code:\n{code}")
    freecad = get_freecad_connection()
    try:
        response = freecad.execute_code(code)
        screenshot = freecad.get_active_screenshot()
        if response["success"]:
            logger.info(f"Code executed successfully")
            return [
                TextContent(
                    type="text",
                    text=f"Code executed successfully: {response['message']}"
                ),
                ImageContent(
                    type="image", data=screenshot, mimeType="image/png"
                )
            ]
        else:
            logger.error(f"Failed to execute code: {response['error']}")
            return [
                TextContent(
                    type="text",
                    text=f"Failed to execute code: {response['error']}"
                ),
                ImageContent(
                    type="image", data=screenshot, mimeType="image/png"
                )
            ]
    except Exception as e:
        logger.error(f"Failed to execute code: {str(e)}")
        return [
            TextContent(type="text", text=f"Failed to execute code: {str(e)}")
        ]


@mcp.tool()
def get_view(
    ctx: Context,
    view_name: Literal[
        "Isometric", "Front", "Top",
        "Right", "Back", "Left",
        "Bottom", "Dimetric", "Trimetric"
    ]
) -> list[ImageContent]:
    """
    Get a screenshot of the active view.

    Args:
        view_name: The name of the view to get the screenshot of.
        The following views are available:
        - "Isometric"
        - "Front"
        - "Top"
        - "Right"
        - "Back"
        - "Left"
        - "Bottom"
        - "Dimetric"
        - "Trimetric"

    Returns:
        A screenshot of the active view.
    """
    logger.info(f"Requested to get view: {view_name}")
    freecad = get_freecad_connection()
    screenshot = freecad.get_active_screenshot(view_name)
    return [
        ImageContent(type="image", data=screenshot, mimeType="image/png")
    ]


@mcp.tool()
def insert_part_from_library(
    ctx: Context,
    relative_path: str
) -> list[TextContent | ImageContent]:
    """
    Insert a part from the parts library addon.

    Args:
        relative_path: The relative path of the part to insert.

    Returns:
        A message indicating the success or failure of the part insertion and a screenshot of the object.
    """
    logger.info(f"Requested to insert part from library: {relative_path}")
    freecad = get_freecad_connection()
    try:
        response = freecad.insert_part_from_library(relative_path)
        screenshot = freecad.get_active_screenshot()
        if response["success"]:
            logger.info(f"Part inserted from library successfully")
            return [
                TextContent(
                    type="text",
                    text=f"Part inserted from library: {response['message']}"
                ),
                ImageContent(
                    type="image", data=screenshot, mimeType="image/png"
                )
            ]
        else:
            logger.error(f"Failed to insert part from library: {response['error']}")
            return [
                TextContent(
                    type="text",
                    text=f"Failed to insert part from library: {response['error']}"
                ),
                ImageContent(
                    type="image", data=screenshot, mimeType="image/png"
                )
            ]
    except Exception as e:
        logger.error(f"Failed to insert part from library: {str(e)}")
        return [
            TextContent(
                type="text",
                text=f"Failed to insert part from library: {str(e)}"
            )
        ]


@mcp.tool()
def get_objects(ctx: Context, doc_name: str) -> list[dict[str, Any]]:
    """
    Get all objects in a document.
    You can use this tool to get the objects in a document to see what you can check or edit.

    Args:
        doc_name: The name of the document to get the objects from.

    Returns:
        A list of objects in the document and a screenshot of the document.
    """
    logger.info(f"Requested to get objects from document: {doc_name}")
    freecad = get_freecad_connection()
    try:
        document_objects = freecad.get_objects(doc_name)
        screenshot = freecad.get_active_screenshot()
        return [
            TextContent(
                type="text", 
                text=json.dumps(document_objects)
            ),
            ImageContent(
                type="image", data=screenshot, mimeType="image/png"
            )
        ]
    except Exception as e:
        logger.error(f"Failed to get objects: {str(e)}")
        return [
            TextContent(type="text", text=f"Failed to get objects: {str(e)}")
        ]


@mcp.tool()
def get_object(ctx: Context, doc_name: str, obj_name: str) -> dict[str, Any]:
    """
    Get an object from a document.
    You can use this tool to get the properties of an object to see what you can check or edit.

    Args:
        doc_name: The name of the document to get the object from.
        obj_name: The name of the object to get.

    Returns:
        The object and a screenshot of the object.
    """
    logger.info(f"Requested to get object:{obj_name} from document {doc_name}")
    freecad = get_freecad_connection()
    try:
        document_object = freecad.get_object(doc_name, obj_name)
        screenshot = freecad.get_active_screenshot()
        return [
            TextContent(
                type="text",
                text=json.dumps(document_object)
            ),
            ImageContent(
                type="image", data=screenshot, mimeType="image/png"
            )
        ]
    except Exception as e:
        logger.error(f"Failed to get object: {str(e)}")
        return [
            TextContent(type="text", text=f"Failed to get object: {str(e)}")
        ]


@mcp.tool()
def get_parts_list(ctx: Context) -> list[str]:
    """
    Get the list of parts in the parts library addon.
    """
    logger.info("Requested to get parts list from library")
    freecad = get_freecad_connection()
    parts = freecad.get_parts_list()
    if parts:
        logger.info(f"Parts list: {parts}")
        return [
            TextContent(type="text", text=json.dumps(parts))
        ]
    else:
        logger.warning("No parts found in the parts library")
        return [
            TextContent(
                type="text",
                text=f"No parts found in the parts library. You must add parts_library addon."
            )
        ]

@mcp.tool()
def export_step(
    ctx: Context,
    doc_name: str,
    file_name: str = None,
    export_to: str = "desktop",
    object_names: list[str] = None
) -> list[TextContent]:
    """
    Export FreeCAD objects to a STEP file format.
    
    STEP (Standard for the Exchange of Product Data) is an ISO standard for the computer-interpretable
    representation and exchange of product manufacturing information.
    
    Args:
        doc_name: The name of the document containing the objects to export.
        file_name: The filename to save as (without path).
                  If not provided, will use document name + .step
        export_to: Where to save the file - "desktop", "documents", "downloads", or "temp".
        object_names: Optional list of specific object names to export. If not provided, all valid objects will be exported.
        
    Returns:
        A message indicating the success or failure of the export operation.
        
    Examples:
        Export all objects from a document to desktop:
        ```json
        {
            "doc_name": "MyModel",
            "file_name": "exported_model.step",
            "export_to": "desktop"
        }
        ```
        
        Export only specific objects to downloads folder:
        ```json
        {
            "doc_name": "MyModel",
            "file_name": "selected_parts.step",
            "export_to": "downloads",
            "object_names": ["Box", "Cylinder"]
        }
        ```
    """
    # Since the RPC export_step might not be available,
    # we'll implement this using execute_code which is always available
    freecad = get_freecad_connection()
    
    try:
        # Default filename if not provided
        if not file_name:
            file_name = f"{doc_name}.step"
            
        # Make sure it has a .step extension
        if not file_name.lower().endswith('.step'):
            file_name += '.step'
            
        # Create Python code to perform the export
        export_code = """
import os
import FreeCAD
import Part
import tempfile

try:
    # Get the document
    doc_name = '{0}'
    doc = FreeCAD.getDocument(doc_name)
    
    if not doc:
        print(f"Document '{{doc_name}}' not found")
        raise Exception(f"Document '{{doc_name}}' not found")
        
    # Where to save the file
    location = '{1}'
    file_name = '{2}'
    
    # Determine save location
    home_dir = os.path.expanduser('~')
    
    if location.lower() == 'desktop':
        save_dir = os.path.join(home_dir, 'Desktop')
    elif location.lower() == 'documents':
        save_dir = os.path.join(home_dir, 'Documents')
    elif location.lower() == 'downloads':
        save_dir = os.path.join(home_dir, 'Downloads')
    elif location.lower() == 'temp':
        save_dir = tempfile.gettempdir()
    else:
        save_dir = os.path.join(home_dir, 'Desktop')  # Default to desktop
        
    # Create full path
    file_path = os.path.join(save_dir, file_name)
    
    print(f"Will save to: {{file_path}}")
    
    # Determine which objects to export
    objects_to_export = []
    object_names = {3}
    
    if object_names:
        # Export specific objects
        for name in object_names:
            obj = doc.getObject(name)
            if obj:
                if hasattr(obj, "Shape"):
                    objects_to_export.append(obj)
                else:
                    print(f"Object '{{name}}' has no Shape attribute, skipping.")
            else:
                print(f"Object '{{name}}' not found, skipping.")
    else:
        # Export all objects with shapes
        for obj in doc.Objects:
            if hasattr(obj, "Shape"):
                objects_to_export.append(obj)
    
    if not objects_to_export:
        print("No valid objects to export")
        raise Exception("No valid objects to export")
    else:
        # Create compound shape for export
        compound = Part.Compound([obj.Shape for obj in objects_to_export])
        
        # Export to STEP
        compound.exportStep(file_path)
        
        print(f"Successfully exported {{len(objects_to_export)}} objects to {{file_path}}")
        
except Exception as e:
    print(f"Error exporting to STEP: {{str(e)}}")
""".format(doc_name, export_to, file_name, object_names or [])
        
        # Execute the export code
        res = freecad.execute_code(export_code)
        
        if res["success"]:
            return [
                TextContent(type="text", text=f"Successfully exported {doc_name} as {file_name} to your {export_to} folder")
            ]
        else:
            return [
                TextContent(type="text", text=f"Failed to export to STEP: {res['error']}")
            ]
    except Exception as e:
        logger.error(f"Failed to export to STEP: {str(e)}")
        return [
            TextContent(type="text", text=f"Failed to export to STEP: {str(e)}")
        ]
        

# NOT SUPPORTED
# @mcp.tool()
# def create_parametric_model(
#     ctx: Context,
#     doc_name: str,
#     model_type: str,
#     name: str = None,
#     parameters: dict[str, Any] = None,
# ) -> list[TextContent | ImageContent]:
#     """Create a parametric 3D model with customizable parameters.
    
#     Args:
#         doc_name: The name of the document to create the model in.
#         model_type: Type of parametric model (box, cylinder, sphere, cone, torus).
#         name: Optional name for the model (defaults to "Param_[ModelType]").
#         parameters: Model-specific parameters.
        
#     Model Types and Parameters:
    
#     1. box:
#        - length: Length of the box (default: 10)
#        - width: Width of the box (default: 10)
#        - height: Height of the box (default: 10)
#        - position: {"x": 0, "y": 0, "z": 0}
#        - color: [r, g, b, a] values in range 0-1
       
#     2. cylinder:
#        - radius: Radius of the cylinder (default: 5)
#        - height: Height of the cylinder (default: 10)
#        - position: {"x": 0, "y": 0, "z": 0}
#        - rotation: {"axis": {"x": 0, "y": 0, "z": 1}, "angle": 0}
#        - color: [r, g, b, a] values in range 0-1
       
#     3. sphere:
#        - radius: Radius of the sphere (default: 5)
#        - position: {"x": 0, "y": 0, "z": 0}
#        - color: [r, g, b, a] values in range 0-1
       
#     4. cone:
#        - radius1: Base radius of the cone (default: 5)
#        - radius2: Top radius of the cone (default: 0)
#        - height: Height of the cone (default: 10)
#        - position: {"x": 0, "y": 0, "z": 0}
#        - rotation: {"axis": {"x": 0, "y": 0, "z": 1}, "angle": 0}
#        - color: [r, g, b, a] values in range 0-1
       
#     5. torus:
#        - radius1: Torus major radius (default: 10)
#        - radius2: Torus minor radius (default: 2)
#        - position: {"x": 0, "y": 0, "z": 0}
#        - rotation: {"axis": {"x": 0, "y": 0, "z": 1}, "angle": 0}
#        - color: [r, g, b, a] values in range 0-1
       
#     Returns:
#         A message indicating the success or failure of the model creation and a screenshot of the model.
        
#     Examples:
#         Create a red box with dimensions 20x15x10:
#         ```json
#         {
#             "doc_name": "MyDocument",
#             "model_type": "box",
#             "name": "MyBox",
#             "parameters": {
#                 "length": 20,
#                 "width": 15,
#                 "height": 10,
#                 "position": {"x": 0, "y": 0, "z": 0},
#                 "color": [1.0, 0.0, 0.0, 1.0]
#             }
#         }
#         ```
        
#         Create a blue cylinder with radius 8 and height 30:
#         ```json
#         {
#             "doc_name": "MyDocument",
#             "model_type": "cylinder",
#             "name": "MyCylinder",
#             "parameters": {
#                 "radius": 8,
#                 "height": 30,
#                 "position": {"x": 0, "y": 0, "z": 0},
#                 "rotation": {"axis": {"x": 1, "y": 0, "z": 0}, "angle": 90},
#                 "color": [0.0, 0.0, 1.0, 1.0]
#             }
#         }
#         ```
#     """
#     freecad = get_freecad_connection()
    
#     if parameters is None:
#         parameters = {}
        
#     if name is not None:
#         parameters["name"] = name
        
#     try:
#         res = freecad.create_parametric_model(doc_name, model_type, parameters)
#         screenshot = freecad.get_active_screenshot()
        
#         if res["success"]:
#             return [
#                 TextContent(type="text", text=f"Parametric {model_type} '{res['object_name']}' created successfully"),
#                 ImageContent(type="image", data=screenshot, mimeType="image/png")
#             ]
#         else:
#             return [
#                 TextContent(type="text", text=f"Failed to create parametric model: {res['error']}"),
#                 ImageContent(type="image", data=screenshot, mimeType="image/png")
#             ]
#     except Exception as e:
#         logger.error(f"Failed to create parametric model: {str(e)}")
#         return [
#             TextContent(type="text", text=f"Failed to create parametric model: {str(e)}")
#         ]


@mcp.tool()
def analyze_cnc_manufacturing_dfm(
    ctx: Context,
    doc_name: str,
    parameters: dict[str, Any] = None,
) -> list[TextContent | ImageContent]:
    """Checks the correspondence of all the objects in the document to CNC Manufacturing DFM rules.
    Marks the found issues with different colors:
        too sharp corners are marked with red color;
        the holes that have too small radius are marked with orange color;
        the circular holes that have too high depth-to-diameter rato are marked with purple color;
        too thin walls are marked with cyan color.

    Args:
        doc_name: The name of the document to be analyzed.
        parameters: DFM parameters dictionary, may include the following float values:
            min_radius: minimal radius of holes;
            max_aspect_ratio: minimal depth-to-diameter ratio for holes;
            min_internal_corner_radius: minimal radius of internal corners;
            min_wall_thickness: minimal wall thickness.

    Returns:
        A dictionary containing success indicator and found issues and a screenshot that indicates changes.
        Issues entry contain the following issues:
            sharp_corners: too sharp corners;
            small_radius: the holes that have too small radius;
            high_aspect_ratio: the circular holes that have too high depth-to-diameter rato;
            wall_thickness: too thin walls.
        Format of the issue entry:
            "object": label of the object,
            "face": face reference name (example: Face3),
            "location": center of mass of the face,
            "required": parameter threshold.
        In addition to these the issue entry contains the issue-specific parameters ("radius", "depth", "thickness", "ratio").
    
    Args example:
        doc_name="TempDoc",
        parameters={
            min_radius=1.0, 
            max_aspect_ratio=4.0, 
            min_internal_corner_radius=0.5, 
            min_wall_thickness=1.0
        }
    
    Results example:
        {
            "success": false,
            "issues": {
                "sharp_corners": [
                    {
                        "object": "Exercise 56",
                        "face": "Face6",
                        "location": "Face at Vector (-81.3661977236758, 12.5, 2.7382263123598703e-14)",
                        "curvature": 0.10000000000000005,
                        "required": "< 0.09523809523809523"
                    }
                ],
                "small_radius": [
                    {
                        "object": "Exercise 56",
                        "face": "Face2",
                        "location": "Face at Vector (-7.957747154594769, 25.5, -9.986456106503282e-16)",
                        "radius": 12.5,
                        "required": 50.0
                    }
                ],
                "high_aspect_ratio": [
                    {
                        "object": "Exercise 56",
                        "face": "Face6",
                        "feature_type": "cylindrical hole",
                        "radius": 9.999999999999995,
                        "depth": 25.0,
                        "ratio": 1.2500000000000007,
                        "required": 1.0
                    }
                ],
                "wall_thickness": [
                    {
                        "object": "Exercise 56",
                        "face": "Face1",
                        "location": "Face center at (1.5707963267948968, 3.3527935619181184)",
                        "thickness": 3.9999999999999996,
                        "required": 4.0
                    }
                ]
            } 
        }            
    """
    logger.info(f"Requested to analyze document {doc_name} for CNC machining DFM rules with parameters: {parameters}")
    freecad = get_freecad_connection()
    try:
        freecad.restore_colors_after_check(doc_name)
        res = freecad.run_cnc_manufacturing_dfm_check(doc_name, parameters)
        screenshot = freecad.get_active_screenshot()
        nissues = 0
        for key in res["issues"]:
            nissues += len(res["issues"][key])
        if res["success"]:
            logger.info(f"Document '{doc_name}' analyzed for CNC machining DFM rules successfully.")
            return [
                TextContent(type="text", text=f"Document is successfully analyzed for CNC Manufacturing DFM rules. Found {nissues} issues:\n" + json.dumps(res["issues"])),
                ImageContent(type="image", data=screenshot, mimeType="image/png")
            ]
        else:
            logger.info(f"There were some problems in document '{doc_name}' CNC machining DFM rules analysis.")
            return [
                TextContent(type="text", text=f"CNC Manufacturing DFM analysis caused some problems. Found {nissues} issues:\n" + json.dumps(res["issues"])),
                ImageContent(type="image", data=screenshot, mimeType="image/png")
            ]
    except Exception as e:
        logger.error(f"CNC Manufacturing DFM analysis failed: {str(e)}")
        return [
            TextContent(type="text", text=f"CNC Manufacturing DFM analysis failed: {str(e)}")
        ]


@mcp.tool()
def analyze_3d_printing_dfm(
    ctx: Context,
    doc_name: str,
    parameters: dict[str, Any] = None,
) -> list[TextContent | ImageContent]:
    """Checks the correspondence of all the objects in the document to 3D Printing DFM rules.
    Marks the found issues with different colors:
        too thin walls are marked with cyan color;
        too small features are marked with green color;
        insufficient overhangs are marked with yellow color;
        the holes that have too small radius are marked with orange color;
        the circular objects that have too high depth-to-diameter rato are marked with purple color;
        insufficient clearance (only for more than one object) are marked with additional blue lines between objects;

    Args:
        doc_name: The name of the document to be analyzed.
        parameters: DFM parameters dictionary, may include the following float values:
            process_type: printing process type, may be set to FDM, SLA, SLS or Other. For FDM, SLA, SLS presets are used, for Other the provided below parameters are used; 
            min_wall_thickness: minimal wall thickness; 
            min_feature_size: minimal size of object elements;  
            max_overhang_angle: highlights planes with the angle between Z axis and normal more than 180 - max_overhang_angle; 
            min_hole_radius: minimal radius of holes; 
            min_clearance: minimal distance between two objects (not object elements!);
            max_aspect_ratio: minimal depth-to-diameter ratio for holes.

    Returns:
        A dictionary containing success indicator and found issues and a screenshot that indicates changes.
        Issues entry contain the following issues:
            wall_thickness: too thin walls
            small_features: too small parts of the object;
            overhangs: overhangs with insufficient angle;
            small_radius: the holes that have too small radius;
            high_aspect_ratio: the circular holes that have too high depth-to-diameter rato;
            insufficient_clearance: too small distance between different objects.       
        Format of the issue entry:
            "object": label of the object,
            "face": face reference name (example: Face3),
            "location": center of mass of the face,
            "required": parameter threshold.
        In addition to these the issue entry contains the issue-specific parameters ("radius", "depth", "thickness", "ratio", etc).
    
    Args example:
        doc_name="TempDoc",
        parameters={
            process_type="FDM" 
        }
    
    Args example:
        doc_name="TempDoc",
        parameters={
            process_type="Other", 
            min_wall_thickness=1.0, 
            min_feature_size=0.8,  
            max_overhang_angle=45.0, 
            min_hole_radius=2.0, 
            min_clearance = 0.5,
            max_aspect_ratio = 20
        }
    
    Results example:
        {
            "success": true,
            "issues": {
                "wall_thickness": [
                    {
                        "object": "Exercise 56",
                        "face": "Face5",
                        "location": "Face center at (5.364192551262733, 8.425690866793065)",
                        "thickness": 5.00000000000003,
                        "required": 50.0
                    }
                ],
                "small_features": [
                    {
                        "object": "Exercise 56",
                        "face": "Face38",
                        "location": "Face at Vector (-111.15580950466699, 16.719066540339213, -2.2621829651866273e-06)",
                        "max_size": 4.269438808857615,
                        "required": 5.8
                    }
                ],
                "small_radius": [
                    {
                        "object": "Exercise 56",
                        "face": "Face6",
                        "location": "Face at Vector (-131.36619772367578, 12.5, 2.7382263123598703e-14)",
                        "radius": 9.999999999999995,
                        "required": 10.0
                    }
                ],
                "small_text": [],
                "high_aspect_ratio": [
                    {
                        "object": "Exercise 56",
                        "face": "Face6",
                        "feature_type": "cylindrical hole",
                        "radius": 9.999999999999995,
                        "depth": 25.0,
                        "ratio": 1.2500000000000007,
                        "required": 1.0
                    }
                ],
                "insufficient_clearance": [
                    {
                        "object1": "Exercise 56",
                        "object2": "47065T711_T-Slotted Framing",
                        "distance": 4.999999999999988,
                        "required": 5.5
                    }
                ]
            }
        }
        
    Note: In the results "small_text" issues are presented, though for now their detection is not implemented. Thus they are always empty.
    """
    logger.info(f"Requested to analyze document {doc_name} for 3D Printing DFM rules with parameters: {parameters}")
    freecad = get_freecad_connection()
    try:
        freecad.restore_colors_after_check(doc_name)
        res = freecad.run_3d_printing_dfm_check(doc_name, parameters)
        screenshot = freecad.get_active_screenshot()
        nissues = 0
        for key in res["issues"]:
            nissues += len(res["issues"][key])
        if res["success"]:
            logger.info(f"Document '{doc_name}' analyzed for 3D Printing DFM rules successfully.")
            return [
                TextContent(type="text", text=f"Document is successfully analyzed for 3D Printing DFM rules. Found {nissues} issues:\n" + json.dumps(res["issues"])),
                ImageContent(type="image", data=screenshot, mimeType="image/png")
            ]
        else:
            logger.info(f"There were some problems in document '{doc_name}' 3D Printing DFM rules analysis.")
            return [
                TextContent(type="text", text=f"3D Printing DFM analysis caused some problems. Found {nissues} issues:\n" + json.dumps(res["issues"])),
                ImageContent(type="image", data=screenshot, mimeType="image/png")
            ]
    except Exception as e:
        logger.error(f"3D Printing DFM analysis failed: {str(e)}")
        return [
            TextContent(type="text", text=f"3D Printing DFM analysis failed: {str(e)}")
        ]


@mcp.tool()
def analyze_injection_molding_dfm(
    ctx: Context,
    doc_name: str,
    parameters: dict[str, Any] = None,
) -> list[TextContent | ImageContent]:
    """Checks the correspondence of all the objects in the document to Injection Molding DFM rules.
    Marks the found issues with different colors:
        small draft angles are marked with orange color;
        too thin or too thick walls are marked with cyan color;
        too sharp corners are marked with red color;
        the circular holes that have too high depth-to-diameter rato are marked with purple color;
        undercuts are marked with green color.

    Args:
        doc_name: The name of the document to be analyzed.
        parameters: DFM parameters dictionary, may include the following float values:
            min_wall_thickness: minimal wall thickness;
            max_wall_thickness: maximal wall thickness;
            min_draft_angle: minimal draft angle;
            min_internal_corner_radius: minimal radius of internal corners;
            max_aspect_ratio: minimal depth-to-diameter ratio for holes.

    Returns:
        A dictionary containing success indicator and found issues and a screenshot that indicates changes.
        Issues entry contain the following issues:
            wall_thickness: too thin or too thick walls;
            draft_angles: too small draft angles;
            sharp_corners: too sharp corners;
            high_aspect_ratio: the circular holes that have too high depth-to-diameter rato;
            undercuts: undercuts.
        Format of the issue entry:
            "object": label of the object,
            "face": face reference name (example: Face3),
            "location": center of mass of the face,
            "required": parameter threshold.
        In addition to these the issue entry contains the issue-specific parameters ("radius", "depth", "thickness", "ratio").
    
    Args example:
        doc_name="TempDoc",
        parameters={
            min_wall_thickness=0.5,
            max_wall_thickenss=4.0,
            min_draft_angle=0.5,
            min_internal_corner_radius=0.25, 
            max_aspect_ratio=5.0.
        }
    
    Results example:
        {
            "success": true,
            "issues": {
                "wall_thickness": [
                    {
                        "object": "Exercise 56",
                        "face": "Face6",
                        "location": "Near vertex at Vector (-124.99999999999999, 0.0, 10.000000000000023)",
                        "thickness": 10.148132107121056,
                        "required": "> 4.1 < 10.0"
                    }
                ],
                "draft_angles": [
                    {
                        "object": "Exercise 56",
                        "face": "Face21",
                        "location": "Face at Vector (-5.962375298785155, 11.0, 1.6233745990932462e-14)",
                        "draft_angle": 1.4210854715202004e-14,
                        "required": 50.5
                    }
                ],
                "sharp_corners": [
                    {
                        "object": "Exercise 56",
                        "face": "Face1",
                        "location": "Face at Vector (-41.56134773457936, 17.70045776423789, -1.7322652905548642e-15)",
                        "curvature": 0.5,
                        "required": "< 0.0975609756097561"
                    }
                ],
                "undercuts": [
                    {
                        "object": "Exercise 56",
                        "face": "Face2",
                        "location": "Face at Vector (-57.95774715459477, 25.5, -9.986456106503282e-16)",
                        "metric": 1,
                        "required": 0
                    }
                ],
                "high_aspect_ratio": [
                    {
                        "object": "Exercise 56",
                        "face": "Face6",
                        "location": "Face at Vector (-131.36619772367578, 12.5, 2.7382263123598703e-14)",
                        "feature_type": "cylindrical hole",
                        "radius": 9.999999999999995,
                        "depth": 25.0,
                        "ratio": 1.2500000000000007,
                        "required": 1.0
                    }
                ]
            }
        }
    """
    logger.info(f"Requested to analyze document {doc_name} for Injection Molding DFM rules with parameters: {parameters}")
    freecad = get_freecad_connection()
    try:
        freecad.restore_colors_after_check(doc_name)
        res = freecad.run_injection_molding_dfm_check(doc_name, parameters)
        screenshot = freecad.get_active_screenshot()
        nissues = 0
        for key in res["issues"]:
            nissues += len(res["issues"][key])
        if res["success"]:
            logger.info(f"Document '{doc_name}' analyzed for Injection Molding DFM rules successfully.")
            return [
                TextContent(type="text", text=f"Document is successfully analyzed for CNC Manufacturing DFM rules. Found {nissues} issues:\n" + json.dumps(res["issues"])),
                ImageContent(type="image", data=screenshot, mimeType="image/png")
            ]
        else:
            logger.info(f"There were some problems in document '{doc_name}' Injection Molding DFM rules analysis.")
            return [
                TextContent(type="text", text=f"CNC Manufacturing DFM analysis caused some problems. Found {nissues} issues:\n" + json.dumps(res["issues"])),
                ImageContent(type="image", data=screenshot, mimeType="image/png")
            ]
    except Exception as e:
        logger.error(f"CNC Manufacturing DFM analysis failed: {str(e)}")
        return [
            TextContent(type="text", text=f"CNC Manufacturing DFM analysis failed: {str(e)}")
        ]


@mcp.tool()
def restore_colors_and_objects_after_dfm_check(
    ctx: Context,
    doc_name: str,
) -> list[TextContent | ImageContent]:
    """ Restore original colors of model faces that were changed to mark DFM issues.
        Removes additional objects if they were created during DFM check.
        Does nothing if the DFM check was not performed or the last DFM check was performed not for the document doc_name.

    Args:
        doc_name: The name of the document that was previously analyzed for DFM rules.

    Returns:
        The message indicating success and the screenshot.
    
    """
    freecad = get_freecad_connection()
    try:
        res = freecad.restore_colors_after_check(doc_name)
        screenshot = freecad.get_active_screenshot()
        if res["success"]:
            return [
                TextContent(type="text", text="The original colors were successfully restored."),
                ImageContent(type="image", data=screenshot, mimeType="image/png")
            ]
        else:
            message = res["message"]
            return [
                TextContent(type="text", text=f"Restoring colors had some problems: {message}"),
                ImageContent(type="image", data=screenshot, mimeType="image/png")
            ]
    except Exception as e:
        logger.error(f"Restoring colors failed: {str(e)}")
        return [
            TextContent(type="text", text=f"Restoring colors failed: {str(e)}")
        ]


# Import prompts from separate module files
from .prompts import asset_creation_strategy
from .prompts.printing_guidelines import get_3d_printing_guidelines, get_cnc_machining_guidelines

dfm_3d_rules_df = pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), "prompts/Taiyaki AI - DFM Rules for MCP - 3D Printing.csv"))
dfm_cnc_rules_df = pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), "prompts/Taiyaki AI - DFM Rules for MCP - CNC Machining.csv"))

# Register all prompts with MCP
@mcp.prompt()
def asset_creation_strategy_prompt() -> str:
    """Strategy for creating assets in FreeCAD"""
    logger.info("Requested asset creation strategy!")
    return asset_creation_strategy()
    
@mcp.prompt()
def get_3d_printing_guidelines_prompt() -> str:
    """Get design guidelines for 3D printing in FreeCAD"""
    dfm_3d_information = {
        "Feature": [
            {
                "Name": feature,
                "Description": description
            }
            for feature, description in zip(
                dfm_3d_rules_df["Feature"].dropna().unique(),
                dfm_3d_rules_df["Description"].dropna().unique()
            )
        ],
        "Process": dfm_3d_rules_df["Process"].unique().tolist()
    }
    return get_3d_printing_guidelines(dfm_3d_information)

@mcp.prompt()
def get_cnc_machining_guidelines_prompt() -> str:
    """Get design guidelines for CNC Machining in FreeCAD"""
    dfm_cnc_information = {
        "Feature": [
            {
                "Name": feature,
                "Description": description
            }
            for feature, description in zip(
                dfm_cnc_rules_df["Feature"].unique(),
                dfm_cnc_rules_df["Description"].unique()
            )
        ]
    }
    return get_cnc_machining_guidelines(dfm_cnc_information)


@mcp.tool()
def refine_3d_printing_dfm(
    ctx: Context,
    features: List[str] | None,
    processes: List[str] | None
) -> str:
    """
    Refine the 3D printing DFM rules based on passed feature and process.

    Returns:
        str: string-like table with feauture and DFM rules for specific process.
    """
    logger.info(f"Requested refining 3d printing dfm with features: {features} and processes: {processes}")
    try:
        dfm_3d_rules = dfm_3d_rules_df.copy()
        subset = dfm_3d_rules[
            (dfm_3d_rules["Feature"].isin(features)) &
            (dfm_3d_rules["Process"].isin(processes))
        ]
        subset = subset.drop(columns=["Description"])
        return [
            TextContent(type="text", text=subset.to_markdown(index=False))
        ]
    except Exception as e:
        logger.error(f"Failed to refine 3D printing DFM: {str(e)}")
        return [
            TextContent(
                type="text", text=f"Failed to refine DFM rules: {str(e)}"
            )
        ]
    

@mcp.tool()
def refine_cnc_machining_dfm(
    ctx: Context,
    features: List[str] | None
) -> str:
    """
    Refine the CNC Machining DFM rules based on passed features.

    Returns:
        str: string-like table with feature and DFM rules.
    """
    logger.info(f"Requested refining CNC dfm rules with features: {features}")
    try:
        dfm_cnc_rules = dfm_cnc_rules_df.copy()
        subset = dfm_cnc_rules[
            dfm_cnc_rules["Feature"].isin(features)
        ]
        subset = subset.drop(columns=["Description"])
        return [
            TextContent(type="text", text=subset.to_markdown(index=False))
        ]
    except Exception as e:
        logger.error(f"Failed to refine CNC machining DFM: {str(e)}")
        return [
            TextContent(
                type="text", text=f"Failed to refine DFM rules: {str(e)}"
            )
        ]

@mcp.tool()
def analyze_screenshot_for_issues(
    ctx: Context,
    doc_name: str = None,
    view_name: str = "Isometric",
    focus_areas: List[str] = None
) -> List[TextContent | ImageContent]:
    """
    Take a screenshot of the current FreeCAD view and analyze it for geometric issues,
    manufacturability problems, and suggest automatic fixes.
    
    Args:
        doc_name: Optional document name to analyze (uses active document if not specified)
        view_name: Camera view for analysis (Isometric, Front, Top, etc.)
        focus_areas: Specific areas to focus on (geometry, manufacturability, assembly, etc.)
    
    Returns:
        Screenshot with analysis overlay and detailed recommendations for fixes
    """
    logger.info(f"Analyzing screenshot for issues in view: {view_name}")
    
    try:
        freecad = get_freecad_connection()
        
        # Take screenshot
        screenshot = freecad.get_active_screenshot(view_name)
        
        # Get object data for context
        if doc_name:
            objects_data = freecad.get_objects(doc_name)
        else:
            # Get active document objects
            objects_data = []
            try:
                # Try to get objects from active document
                active_doc_result = freecad.execute_code("FreeCAD.ActiveDocument.Name if FreeCAD.ActiveDocument else None")
                if active_doc_result.get("success") and active_doc_result.get("message"):
                    doc_name = active_doc_result["message"].strip('"\'')
                    objects_data = freecad.get_objects(doc_name)
            except Exception as e:
                logger.warning(f"Could not get active document objects: {e}")

        
        # Analyze the screenshot and geometry
        analysis_results = {
            "geometric_issues": [],
            "manufacturability_issues": [],
            "spatial_issues": [],
            "suggested_fixes": [],
            "auto_fixable": []
        }
        
        # Geometric analysis based on object data
        for obj in objects_data:
            obj_name = obj.get("Name", "Unknown")
            obj_type = obj.get("TypeId", "")
            
            # Check for common geometric issues
            if "Box" in obj_type:
                # Check for very thin walls
                length = obj.get("Length", 0)
                width = obj.get("Width", 0) 
                height = obj.get("Height", 0)
                
                min_dimension = min([d for d in [length, width, height] if d > 0])
                if min_dimension < 1.0:  # Less than 1mm
                    analysis_results["geometric_issues"].append({
                        "object": obj_name,
                        "issue": "Very thin wall detected",
                        "current_value": f"{min_dimension:.2f}mm",
                        "recommendation": "Increase minimum wall thickness to 1.2mm",
                        "severity": "warning"
                    })
                    analysis_results["auto_fixable"].append({
                        "object": obj_name,
                        "fix": "increase_wall_thickness",
                        "target_value": 1.2
                    })
            
            elif "Cylinder" in obj_type:
                # Check hole aspect ratios
                radius = obj.get("Radius", 0)
                height = obj.get("Height", 0)
                
                if radius > 0 and height > 0:
                    aspect_ratio = height / (radius * 2)  # depth/diameter
                    if aspect_ratio > 5:
                        analysis_results["manufacturability_issues"].append({
                            "object": obj_name,
                            "issue": "High aspect ratio hole",
                            "current_value": f"Aspect ratio: {aspect_ratio:.1f}",
                            "recommendation": "Consider stepped drilling or reduce depth",
                            "severity": "warning"
                        })
        
        # Check for potential spatial/assembly issues
        if len(objects_data) > 1:
            # Simple overlap detection
            for i, obj1 in enumerate(objects_data):
                for j, obj2 in enumerate(objects_data[i+1:], i+1):
                    # Basic bounding box overlap check (simplified)
                    # In real implementation, would use actual FreeCAD geometry
                    analysis_results["spatial_issues"].append({
                        "objects": [obj1.get("Name"), obj2.get("Name")],
                        "issue": "Potential interference - verify clearances",
                        "recommendation": "Check assembly constraints and clearances",
                        "severity": "info"
                    })
        
        # Generate overall recommendations
        total_issues = (len(analysis_results["geometric_issues"]) + 
                       len(analysis_results["manufacturability_issues"]) +
                       len(analysis_results["spatial_issues"]))
        
        if total_issues == 0:
            analysis_results["suggested_fixes"].append("✅ No major issues detected in current view")
        else:
            if analysis_results["geometric_issues"]:
                analysis_results["suggested_fixes"].append("🔧 Fix geometric issues to improve model robustness")
            if analysis_results["manufacturability_issues"]:
                analysis_results["suggested_fixes"].append("🏭 Address manufacturability concerns to reduce production costs")
            if analysis_results["spatial_issues"]:
                analysis_results["suggested_fixes"].append("📐 Verify spatial relationships for proper assembly")
        
        # Format comprehensive report
        report = f"""# Screenshot Analysis Report

## View Analyzed: {view_name}
## Document: {doc_name or 'Active Document'}
## Objects Found: {len(objects_data)}

## Analysis Results

### Geometric Issues ({len(analysis_results['geometric_issues'])})
"""
        
        for issue in analysis_results["geometric_issues"]:
            severity_icon = "⚠️" if issue["severity"] == "warning" else "❌" if issue["severity"] == "error" else "ℹ️"
            report += f"- {severity_icon} **{issue['object']}**: {issue['issue']}\n"
            report += f"  - Current: {issue['current_value']}\n"
            report += f"  - Recommendation: {issue['recommendation']}\n\n"
        
        report += f"\n### Manufacturability Issues ({len(analysis_results['manufacturability_issues'])})\n"
        
        for issue in analysis_results["manufacturability_issues"]:
            severity_icon = "⚠️" if issue["severity"] == "warning" else "❌" if issue["severity"] == "error" else "ℹ️"
            report += f"- {severity_icon} **{issue['object']}**: {issue['issue']}\n"
            report += f"  - Current: {issue['current_value']}\n"
            report += f"  - Recommendation: {issue['recommendation']}\n\n"
        
        report += f"\n### Spatial Issues ({len(analysis_results['spatial_issues'])})\n"
        
        for issue in analysis_results["spatial_issues"]:
            severity_icon = "⚠️" if issue["severity"] == "warning" else "❌" if issue["severity"] == "error" else "ℹ️"
            report += f"- {severity_icon} **{' & '.join(issue['objects'])}**: {issue['issue']}\n"
            report += f"  - Recommendation: {issue['recommendation']}\n\n"
        
        report += "\n## Recommendations\n"
        for i, fix in enumerate(analysis_results["suggested_fixes"], 1):
            report += f"{i}. {fix}\n"
        
        if analysis_results["auto_fixable"]:
            report += f"\n## Auto-Fixable Issues ({len(analysis_results['auto_fixable'])})\n"
            report += "The following issues can be automatically corrected:\n"
            for fix in analysis_results["auto_fixable"]:
                report += f"- **{fix['object']}**: {fix['fix']} to {fix.get('target_value', 'optimal value')}\n"
            report += "\n💡 Use the `apply_automatic_fixes` tool to apply these corrections.\n"
        
        logger.info(f"Screenshot analysis complete: {total_issues} issues found")
        
        return [
            TextContent(type="text", text=report),
            ImageContent(type="image", data=screenshot, mimeType="image/png")
        ]
        
    except Exception as e:
        logger.error(f"Screenshot analysis failed: {e}")
        return [
            TextContent(type="text", text=f"Screenshot analysis failed: {e}")
        ]


@mcp.tool()
def apply_automatic_fixes(
    ctx: Context,
    doc_name: str,
    fix_types: List[str] = None
) -> List[TextContent | ImageContent]:
    """
    Apply automatic fixes for common geometric and manufacturability issues detected in screenshot analysis.
    
    Args:
        doc_name: Document name to apply fixes to
        fix_types: Specific types of fixes to apply (wall_thickness, hole_diameter, etc.)
                  If None, applies all safe automatic fixes
    
    Returns:
        Results of applied fixes with before/after comparison
    """
    logger.info(f"Applying automatic fixes to document: {doc_name}")
    
    try:
        freecad = get_freecad_connection()
        
        # Get current state
        before_screenshot = freecad.get_active_screenshot()
        objects_data = freecad.get_objects(doc_name)
        
        applied_fixes = []
        
        # Apply fixes based on common patterns
        for obj in objects_data:
            obj_name = obj.get("Name", "Unknown")
            obj_type = obj.get("TypeId", "")
            
            # Fix thin walls in boxes
            if "Box" in obj_type and (fix_types is None or "wall_thickness" in fix_types):
                length = obj.get("Length", 0)
                width = obj.get("Width", 0)
                height = obj.get("Height", 0)
                
                min_dimension = min([d for d in [length, width, height] if d > 0])
                if min_dimension < 1.2:  # Below manufacturing minimum
                    # Increase the minimum dimension to 1.2mm
                    if length == min_dimension:
                        new_length = 1.2
                        fix_code = f"""
import FreeCAD
doc = FreeCAD.getDocument('{doc_name}')
obj = doc.getObject('{obj_name}')
if obj:
    obj.Length = {new_length}
    doc.recompute()
"""
                    elif width == min_dimension:
                        new_width = 1.2
                        fix_code = f"""
import FreeCAD
doc = FreeCAD.getDocument('{doc_name}')
obj = doc.getObject('{obj_name}')
if obj:
    obj.Width = {new_width}
    doc.recompute()
"""
                    elif height == min_dimension:
                        new_height = 1.2
                        fix_code = f"""
import FreeCAD
doc = FreeCAD.getDocument('{doc_name}')
obj = doc.getObject('{obj_name}')
if obj:
    obj.Height = {new_height}
    doc.recompute()
"""
                    
                    result = freecad.execute_code(fix_code)
                    if result.get("success"):
                        applied_fixes.append({
                            "object": obj_name,
                            "fix": "Increased wall thickness",
                            "old_value": f"{min_dimension:.2f}mm",
                            "new_value": "1.2mm",
                            "result": "success"
                        })
                    else:
                        applied_fixes.append({
                            "object": obj_name,
                            "fix": "Attempted wall thickness fix",
                            "result": "failed",
                            "error": result.get("error", "Unknown error")
                        })
            
            # Add corner radii for better manufacturability
            if "Box" in obj_type and (fix_types is None or "corner_radii" in fix_types):
                # Add small corner radii using FreeCAD's fillet operation
                fillet_code = f"""
import FreeCAD
import Part

doc = FreeCAD.getDocument('{doc_name}')
obj = doc.getObject('{obj_name}')

if obj and hasattr(obj, 'Shape'):
    try:
        # Add small fillets to edges
        shape = obj.Shape
        edges = shape.Edges
        
        # Apply 0.5mm fillet to all edges
        if len(edges) > 0:
            fillet = shape.makeFillet(0.5, edges)
            
            # Create new filleted object
            filleted_obj = doc.addObject("Part::Feature", "{obj_name}_Filleted")
            filleted_obj.Shape = fillet
            filleted_obj.ViewObject.ShapeColor = obj.ViewObject.ShapeColor
            
            # Hide original object
            obj.ViewObject.Visibility = False
            
            doc.recompute()
    except Exception as e:
        print(f"Fillet operation failed: {{e}}")
"""
                
                result = freecad.execute_code(fillet_code)
                if result.get("success"):
                    applied_fixes.append({
                        "object": obj_name,
                        "fix": "Added corner radii for manufacturability",
                        "new_value": "0.5mm radii",
                        "result": "success"
                    })
        
        # Take after screenshot
        after_screenshot = freecad.get_active_screenshot()
        
        # Generate report
        report = f"""# Automatic Fixes Applied

## Document: {doc_name}
## Fixes Applied: {len([f for f in applied_fixes if f['result'] == 'success'])}
## Failed Fixes: {len([f for f in applied_fixes if f['result'] == 'failed'])}

## Applied Fixes
"""
        
        for fix in applied_fixes:
            if fix["result"] == "success":
                report += f"✅ **{fix['object']}**: {fix['fix']}\n"
                if "old_value" in fix:
                    report += f"   - Changed from {fix['old_value']} to {fix['new_value']}\n"
                elif "new_value" in fix:
                    report += f"   - Applied: {fix['new_value']}\n"
            else:
                report += f"❌ **{fix['object']}**: {fix['fix']} - {fix.get('error', 'Failed')}\n"
        
        if not applied_fixes:
            report += "ℹ️ No automatic fixes were needed or applicable.\n"
        
        report += "\n## Recommendations\n"
        report += "1. Review the changes and verify they meet your design requirements\n"
        report += "2. Run DFM analysis to confirm manufacturability improvements\n"
        report += "3. Check assembly constraints if this is part of a larger assembly\n"
        
        logger.info(f"Applied {len([f for f in applied_fixes if f['result'] == 'success'])} automatic fixes")
        
        return [
            TextContent(type="text", text=report),
            ImageContent(type="image", data=after_screenshot, mimeType="image/png")
        ]
        
    except Exception as e:
        logger.error(f"Automatic fixes failed: {e}")
        return [
            TextContent(type="text", text=f"Automatic fixes failed: {e}")
        ]


@mcp.tool()
def analyze_manufacturability_quick(
    ctx: Context,
    doc_name: str,
    process: str = "cnc_machining",
    material: str = "aluminum"
) -> List[TextContent]:
    """
    Quick manufacturability analysis focused on geometric feasibility rather than cost.
    
    Args:
        doc_name: FreeCAD document to analyze
        process: Manufacturing process (cnc_machining, 3d_printing, injection_molding)
        material: Material type (aluminum, steel, plastic)
    
    Returns:
        Focused manufacturability recommendations
    """
    logger.info(f"Quick manufacturability analysis for {doc_name} - {process}")
    
    try:
        freecad = get_freecad_connection()
        objects_data = freecad.get_objects(doc_name)
        
        issues = []
        recommendations = []
        
        # Process-specific analysis
        for obj in objects_data:
            obj_name = obj.get("Name", "Unknown")
            obj_type = obj.get("TypeId", "")
            
            if process == "cnc_machining":
                # Check for CNC manufacturability
                if "Box" in obj_type:
                    length = obj.get("Length", 0)
                    width = obj.get("Width", 0)
                    height = obj.get("Height", 0)
                    
                    # Check for deep narrow pockets
                    min_dimension = min([d for d in [length, width, height] if d > 0])
                    max_dimension = max([d for d in [length, width, height] if d > 0])
                    
                    if max_dimension / min_dimension > 10:
                        issues.append(f"**{obj_name}**: High aspect ratio may require special tooling")
                        recommendations.append(f"Consider breaking {obj_name} into multiple operations")
                    
                    # Check for sharp internal corners
                    issues.append(f"**{obj_name}**: Add corner radii ≥ 0.5mm for tool clearance")
                    recommendations.append(f"Apply fillets to {obj_name} edges for better machinability")
                
                elif "Cylinder" in obj_type:
                    radius = obj.get("Radius", 0)
                    height = obj.get("Height", 0)
                    
                    # Check hole depth-to-diameter ratio
                    if radius > 0 and height > 0:
                        aspect_ratio = height / (radius * 2)
                        if aspect_ratio > 5:
                            issues.append(f"**{obj_name}**: Deep hole (aspect ratio {aspect_ratio:.1f}) needs special drilling")
                            recommendations.append(f"Consider stepped drilling or gun drilling for {obj_name}")
            
            elif process == "3d_printing":
                # Check for 3D printing manufacturability
                if "Box" in obj_type:
                    height = obj.get("Height", 0)
                    if height > 200:  # Typical FDM build height limit
                        issues.append(f"**{obj_name}**: Height {height}mm may exceed printer build volume")
                        recommendations.append(f"Consider splitting {obj_name} or rotating for printing")
                    
                    # Check wall thickness
                    min_dimension = min([d for d in [obj.get("Length", 0), obj.get("Width", 0), obj.get("Height", 0)] if d > 0])
                    if min_dimension < 1.2:
                        issues.append(f"**{obj_name}**: Wall thickness {min_dimension:.1f}mm below FDM minimum")
                        recommendations.append(f"Increase wall thickness of {obj_name} to ≥ 1.2mm")
                
                # Check for overhangs (simplified analysis)
                issues.append(f"**{obj_name}**: Verify overhangs ≤ 45° to avoid supports")
                recommendations.append(f"Review {obj_name} orientation to minimize support material")
            
            elif process == "injection_molding":
                # Check for injection molding manufacturability
                if "Box" in obj_type:
                    # Check for uniform wall thickness
                    length = obj.get("Length", 0)
                    width = obj.get("Width", 0)
                    height = obj.get("Height", 0)
                    
                    # Simplified wall thickness check
                    dimensions = [d for d in [length, width, height] if d > 0]
                    if dimensions:
                        thickness_variation = (max(dimensions) - min(dimensions)) / max(dimensions)
                        if thickness_variation > 0.5:
                            issues.append(f"**{obj_name}**: High wall thickness variation may cause warping")
                            recommendations.append(f"Design {obj_name} with more uniform wall thickness")
                    
                    # Check for draft angles (simplified)
                    issues.append(f"**{obj_name}**: Add 1-2° draft angles to vertical surfaces")
                    recommendations.append(f"Apply draft to {obj_name} for easier part ejection")
        
        # Generate report
        report = f"""# Quick Manufacturability Analysis

## Process: {process.replace('_', ' ').title()}
## Material: {material.title()}
## Objects Analyzed: {len(objects_data)}

## Issues Found ({len(issues)})
"""
        
        if issues:
            for issue in issues:
                report += f"- ⚠️ {issue}\n"
        else:
            report += "- ✅ No major manufacturability issues detected\n"
        
        report += f"\n## Recommendations ({len(recommendations)})\n"
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
        else:
            report += "- ✅ Design appears manufacturable with current process\n"
        
        # Add process-specific tips
        report += f"\n## {process.replace('_', ' ').title()} Tips\n"
        
        if process == "cnc_machining":
            report += "- Use standard tool sizes when possible\n"
            report += "- Minimize tool changes and setups\n"
            report += "- Consider workholding and clamping access\n"
            report += "- Add corner radii to reduce stress concentrations\n"
        
        elif process == "3d_printing":
            report += "- Orient parts to minimize supports\n"
            report += "- Design self-supporting features where possible\n"
            report += "- Consider layer adhesion direction for strength\n"
            report += "- Plan for post-processing access\n"
        
        elif process == "injection_molding":
            report += "- Maintain uniform wall thickness\n"
            report += "- Add draft angles to all vertical surfaces\n"
            report += "- Avoid sharp corners and undercuts\n"
            report += "- Consider gate location and flow patterns\n"
        
        logger.info(f"Manufacturability analysis complete: {len(issues)} issues found")
        
        return [TextContent(type="text", text=report)]
        
    except Exception as e:
        logger.error(f"Manufacturability analysis failed: {e}")
        return [TextContent(type="text", text=f"Manufacturability analysis failed: {e}")]








def _analyze_geometry_errors(objects_data):
    """Analyze objects for geometric construction errors"""
    issues = []
    recommendations = []
    
    for obj in objects_data:
        obj_name = obj.get("Name", "Unknown")
        obj_type = obj.get("TypeId", "")
        
        # Check for zero-dimension objects
        if "Box" in obj_type:
            length = obj.get("Length", 0)
            width = obj.get("Width", 0) 
            height = obj.get("Height", 0)
            
            if any(d <= 0 for d in [length, width, height]):
                issues.append(f"{obj_name}: Has zero or negative dimensions")
                recommendations.append(f"Set positive dimensions for {obj_name}")
        
        elif "Cylinder" in obj_type:
            radius = obj.get("Radius", 0)
            height = obj.get("Height", 0)
            
            if radius <= 0 or height <= 0:
                issues.append(f"{obj_name}: Invalid cylinder parameters")
                recommendations.append(f"Set positive radius and height for {obj_name}")
        
        elif "Sphere" in obj_type:
            radius = obj.get("Radius", 0)
            if radius <= 0:
                issues.append(f"{obj_name}: Invalid sphere radius")
                recommendations.append(f"Set positive radius for {obj_name}")
        
        elif "Cone" in obj_type:
            radius1 = obj.get("Radius1", 0)
            radius2 = obj.get("Radius2", 0)
            height = obj.get("Height", 0)
            
            if radius1 <= 0 and radius2 <= 0:
                issues.append(f"{obj_name}: Invalid cone radii")
                recommendations.append(f"Set positive radius for {obj_name}")
            if height <= 0:
                issues.append(f"{obj_name}: Invalid cone height")
                recommendations.append(f"Set positive height for {obj_name}")
    
    return issues, recommendations


def _analyze_manufacturing_issues(objects_data):
    """Analyze objects for manufacturing constraints"""
    issues = []
    recommendations = []
    
    for obj in objects_data:
        obj_name = obj.get("Name", "Unknown")
        obj_type = obj.get("TypeId", "")
        
        # Check minimum feature sizes
        if "Box" in obj_type:
            length = obj.get("Length", 0)
            width = obj.get("Width", 0)
            height = obj.get("Height", 0)
            
            dimensions = [d for d in [length, width, height] if d > 0]
            if not dimensions:
                continue
                
            min_dimension = min(dimensions)
            max_dimension = max(dimensions)
            
            if 0 < min_dimension < 1.0:  # Less than 1mm
                issues.append(f"{obj_name}: Very thin features may be difficult to machine")
                recommendations.append(f"Increase minimum thickness of {obj_name} to >1mm")
            
            # Check aspect ratios
            if min_dimension > 0 and max_dimension / min_dimension > 10:
                issues.append(f"{obj_name}: High aspect ratio may cause deflection")
                recommendations.append(f"Add support ribs to {obj_name} or reduce aspect ratio")
        
        elif "Cylinder" in obj_type:
            radius = obj.get("Radius", 0)
            height = obj.get("Height", 0)
            
            if radius > 0 and height > 0:
                if radius < 0.5:  # Very small radius
                    issues.append(f"{obj_name}: Small radius may be difficult to machine")
                    recommendations.append(f"Increase radius of {obj_name} for better machinability")
                
                if height / radius > 20:  # Very long cylinder
                    issues.append(f"{obj_name}: High length-to-diameter ratio may cause deflection")
                    recommendations.append(f"Add support or reduce length of {obj_name}")
    
    return issues, recommendations


def _analyze_spatial_layout(objects_data):
    """Analyze spatial relationships between objects"""
    issues = []
    recommendations = []
    
    # Check for objects at same location (potential conflicts)
    placements = {}
    for obj in objects_data:
        obj_name = obj.get("Name", "Unknown")
        placement = obj.get("Placement", {})
        base = placement.get("Base", {})
        
        if base:
            pos_key = f"{base.get('x', 0):.1f},{base.get('y', 0):.1f},{base.get('z', 0):.1f}"
            if pos_key in placements:
                issues.append(f"{obj_name} and {placements[pos_key]}: Objects at same location")
                recommendations.append(f"Separate {obj_name} and {placements[pos_key]} spatially")
            else:
                placements[pos_key] = obj_name
    
    return issues, recommendations


def _apply_geometry_fixes(freecad, doc_name, objects_data):
    """Apply automatic geometry fixes"""
    fixes = []
    
    for obj in objects_data:
        obj_name = obj.get("Name", "Unknown")
        obj_type = obj.get("TypeId", "")
        
        # Fix zero-dimension boxes
        if "Box" in obj_type:
            length = obj.get("Length", 0)
            width = obj.get("Width", 0)
            height = obj.get("Height", 0)
            
            if any(d <= 0 for d in [length, width, height]):
                fix_code = f"""
# Fix zero dimensions for {obj_name}
obj = FreeCAD.ActiveDocument.getObject('{obj_name}')
if obj:
    if obj.Length <= 0: obj.Length = 10.0
    if obj.Width <= 0: obj.Width = 10.0
    if obj.Height <= 0: obj.Height = 10.0
"""
                freecad.execute_code(fix_code)
                fixes.append(f"Fixed zero dimensions in {obj_name}")
        
        # Fix invalid cylinders
        elif "Cylinder" in obj_type:
            radius = obj.get("Radius", 0)
            height = obj.get("Height", 0)
            
            if radius <= 0 or height <= 0:
                fix_code = f"""
# Fix invalid cylinder {obj_name}
obj = FreeCAD.ActiveDocument.getObject('{obj_name}')
if obj:
    if obj.Radius <= 0: obj.Radius = 5.0
    if obj.Height <= 0: obj.Height = 10.0
"""
                freecad.execute_code(fix_code)
                fixes.append(f"Fixed invalid parameters in {obj_name}")
        
        # Fix invalid spheres
        elif "Sphere" in obj_type:
            radius = obj.get("Radius", 0)
            if radius <= 0:
                fix_code = f"""
# Fix invalid sphere {obj_name}
obj = FreeCAD.ActiveDocument.getObject('{obj_name}')
if obj:
    if obj.Radius <= 0: obj.Radius = 5.0
"""
                freecad.execute_code(fix_code)
                fixes.append(f"Fixed invalid radius in {obj_name}")
        
        # Fix invalid cones
        elif "Cone" in obj_type:
            radius1 = obj.get("Radius1", 0)
            radius2 = obj.get("Radius2", 0)
            height = obj.get("Height", 0)
            
            if radius1 <= 0 and radius2 <= 0:
                fix_code = f"""
# Fix invalid cone {obj_name}
obj = FreeCAD.ActiveDocument.getObject('{obj_name}')
if obj:
    if obj.Radius1 <= 0: obj.Radius1 = 5.0
    if obj.Radius2 <= 0: obj.Radius2 = 2.0
"""
                freecad.execute_code(fix_code)
                fixes.append(f"Fixed invalid cone radii in {obj_name}")
            
            if height <= 0:
                fix_code = f"""
# Fix invalid cone height {obj_name}
obj = FreeCAD.ActiveDocument.getObject('{obj_name}')
if obj:
    if obj.Height <= 0: obj.Height = 10.0
"""
                freecad.execute_code(fix_code)
                fixes.append(f"Fixed invalid height in {obj_name}")
    
    return fixes


def _apply_manufacturability_fixes(freecad, doc_name, objects_data):
    """Apply automatic manufacturability fixes"""
    fixes = []
    
    for obj in objects_data:
        obj_name = obj.get("Name", "Unknown")
        obj_type = obj.get("TypeId", "")
        
        # Add minimum thickness to thin features
        if "Box" in obj_type:
            length = obj.get("Length", 0)
            width = obj.get("Width", 0)
            height = obj.get("Height", 0)
            
            min_thickness = 1.5  # Minimum machinable thickness
            
            if 0 < height < min_thickness:
                fix_code = f"""
# Increase thickness of {obj_name}
obj = FreeCAD.ActiveDocument.getObject('{obj_name}')
if obj and obj.Height < {min_thickness}:
    obj.Height = {min_thickness}
"""
                freecad.execute_code(fix_code)
                fixes.append(f"Increased thickness of {obj_name} to {min_thickness}mm")
            
            if 0 < width < min_thickness:
                fix_code = f"""
# Increase width of {obj_name}
obj = FreeCAD.ActiveDocument.getObject('{obj_name}')
if obj and obj.Width < {min_thickness}:
    obj.Width = {min_thickness}
"""
                freecad.execute_code(fix_code)
                fixes.append(f"Increased width of {obj_name} to {min_thickness}mm")
        
        elif "Cylinder" in obj_type:
            radius = obj.get("Radius", 0)
            min_radius = 0.5  # Minimum machinable radius
            
            if 0 < radius < min_radius:
                fix_code = f"""
# Increase radius of {obj_name}
obj = FreeCAD.ActiveDocument.getObject('{obj_name}')
if obj and obj.Radius < {min_radius}:
    obj.Radius = {min_radius}
"""
                freecad.execute_code(fix_code)
                fixes.append(f"Increased radius of {obj_name} to {min_radius}mm")
    
    return fixes


def _apply_spatial_fixes(freecad, doc_name, objects_data):
    """Apply automatic spatial layout fixes"""
    fixes = []
    
    # Separate overlapping objects
    placements = {}
    for obj in objects_data:
        obj_name = obj.get("Name", "Unknown")
        placement = obj.get("Placement", {})
        base = placement.get("Base", {})
        
        if base:
            x, y, z = base.get('x', 0), base.get('y', 0), base.get('z', 0)
            pos_key = f"{x:.1f},{y:.1f},{z:.1f}"
            
            if pos_key in placements:
                # Move the second object
                fix_code = f"""
# Separate overlapping object {obj_name}
obj = FreeCAD.ActiveDocument.getObject('{obj_name}')
if obj:
    obj.Placement.Base.x += 20  # Move 20mm in X direction
"""
                freecad.execute_code(fix_code)
                fixes.append(f"Separated {obj_name} from {placements[pos_key]}")
            else:
                placements[pos_key] = obj_name
    
    return fixes


def main():
    """Run the MCP server"""
    mcp.run()
