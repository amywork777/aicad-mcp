from typing import Any
from dataclasses import dataclass, field
import FreeCAD as App
import FreeCADGui as Gui

import json
import tempfile, os, base64
import pandas as pd

from dfm.base_checker import restore_original_colors, remove_additional_objects
from dfm.cnc_check12 import run_cnc_dfm_checker
from dfm.tdp_check3 import run_tdp_dfm_checker
from dfm.injectm_check3 import run_im_dfm_checker
from utils.serialize import serialize_object
from utils.parts import insert_part_from_library, get_parts_list
from .rpc_proxy import RPCProxy
from prompts.printing_guidelines import get_3d_printing_guidelines, get_cnc_machining_guidelines, get_injection_molding_guidelines

@dataclass
class Object:
    name: str
    type: str | None = None
    analysis: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)

class FreeCADRPC:
    def __init__(self):
        self.proxy = RPCProxy()
        self.colors_storage = {}
        self.additional_objects = {}

        base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.dfm_3d_rules_df = pd.read_csv(os.path.join(base_dir, "prompts/Taiyaki AI - DFM Rules for MCP - 3D Printing.csv"))
        self.dfm_cnc_rules_df = pd.read_csv(os.path.join(base_dir, "prompts/Taiyaki AI - DFM Rules for MCP - CNC Machining.csv"))
        self.dfm_im_rules_df = pd.read_csv(os.path.join(base_dir, "prompts/Taiyaki AI - DFM Rules for MCP - Injection Molding.csv"))

    def ping(self):
        """Simple health check to verify the RPC service is responsive."""
        return True

    def list_documents(self):
        """Returns a list of all currently open FreeCAD document names."""
        return list(App.listDocuments().keys())

    def create_document(self, name: str):
        """
        Creates a new FreeCAD document with the given name.

        Args:
            name: The name of the new document.

        Returns:
            A dict indicating success and the created document name.
        """
        def task():
            App.newDocument(name)
            return {"success": True, "document_name": name}
        return self.proxy.run(task)
 
    def create_object(self, doc_name: str, params_json: str) -> dict:
        """
        Creates a new FreeCAD object in the specified document using JSON parameters.

        Args:
            doc_name (str): Name of the target FreeCAD document.
            params_json (str): JSON string with the following structure:
                {
                "Name": str,              # Object name
                "Type": str,              # FreeCAD type (e.g., "Part::Box", "Fem::ConstraintFixed")
                "Analysis": Optional[str],# FEM analysis to associate with, if applicable
                "Properties": dict        # Key-value pairs for object properties
                }

                Example:
                {
                "Name": "MyBox",
                "Type": "Part::Box",
                "Properties": {
                    "Length": 10.0,
                    "Width": 10.0,
                    "Height": 5.0,
                    "ShapeColor": [0.3, 0.4, 0.9, 1.0],
                    "Placement": {
                    "Base": {"x": 0, "y": 0, "z": 0},
                    "Rotation": {
                        "Axis": {"x": 0, "y": 0, "z": 1},
                        "Angle": 45
                    }
                    }
                }
                }

        Returns:
            dict: {
                "success": bool,
                "object_name": str,
                "error": Optional[str]
            }
        """
        params = json.loads(params_json)
        def task():
            doc = App.getDocument(doc_name)
            if not doc:
                return {"success": False, "error": f"Document '{doc_name}' not found."}
            
            obj = Object(
                name=params.get("Name", "New_Object"),
                type=params.get("Type", None),
                analysis=params.get("Analysis", None),
                properties=params.get("Properties", {}),
            )

            status = self._create_object_gui(doc_name, obj)
            return {"success": status, "object_name": obj.name}
        return self.proxy.run(task)

    def edit_object(self, doc_name: str, obj_name: str, params_json: str):
        """
        Edits an existing FreeCAD object by updating its properties.

        Args:
            doc_name (str): The document where the object is located.
            obj_name (str): The name of the object to be modified.
            params_json (str): JSON string of properties to update.
                This JSON should be of the form:
                {
                "Length": 15.0,
                "ShapeColor": [1.0, 0.0, 0.0, 1.0],
                "Placement": {
                    "Base": {"x": 5, "y": 0, "z": 0},
                    "Rotation": {
                    "Axis": {"x": 0, "y": 1, "z": 0},
                    "Angle": 90
                    }
                }
                }

        Returns:
            dict: {
                "success": bool,
                "object_name": str,
                "error": Optional[str]
            }
        """
        params = json.loads(params_json)
        def task():
            doc = App.getDocument(doc_name)
            if not doc:
                return {"success": False, "error": f"Document '{doc_name}' not found."}
            
            obj = Object(
                name=obj_name,
                # properties=properties.get("Properties", {}),
                properties=params,
            )

            status = self._edit_object_gui(doc_name, obj)
            return {"success": status, "object_name": obj.name}
        return self.proxy.run(task)

    def delete_object(self, doc_name: str, obj_name: str):
        """
        Deletes an object from the specified document.

        Args:
            doc_name: The document name.
            obj_name: The name of the object to delete.

        Returns:
            Dict with success status and object name.
        """
        def task():
            doc = App.getDocument(doc_name)
            if not doc:
                return {"success": False, "error": f"Document '{doc_name}' not found."}
            
            status = self._delete_object_gui(doc_name, obj_name)

            return {"success": status, "object_name": obj_name}
        return self.proxy.run(task)

    def export_step(self, doc_name: str, file_path: str):
        """
        Exports all valid shapes in a document to a single STEP file.

        Args:
            doc_name: FreeCAD document name.
            file_path: Full file path to export the STEP file to.

        Returns:
            Dict with success flag and export path or error message.
        """
        def task():
            import Part
            doc = App.getDocument(doc_name)
            if not doc:
                return {"success": False, "error": f"Document '{doc_name}' not found."}
            objs = [o for o in doc.Objects if hasattr(o, "Shape")]
            if not objs:
                return {"success": False, "error": "No valid objects to export."}
            shape = Part.Compound([o.Shape for o in objs])
            shape.exportStep(file_path)
            return {"success": True, "file_path": file_path}
        return self.proxy.run(task)

    def insert_part_from_library(self, relative_path: str):
        """
        Inserts a part from a predefined library into the active document.

        Args:
            relative_path: Relative path to the part in the library.

        Returns:
            Dict indicating success and a message.
        """
        return self.proxy.run(lambda: insert_part_from_library(relative_path) or {"success": True, "message": "Part inserted."})

    def get_parts_list(self):
        """
        Retrieves a list of available parts from the internal part library.

        Returns:
            List of parts with metadata (name, category, path).
        """
        return get_parts_list()

    def get_objects(self, doc_name: str):
        """
        Returns serialized data for all objects in a given document.

        Args:
            doc_name: Name of the document.

        Returns:
            List of serialized object dictionaries.
        """
        doc = App.getDocument(doc_name)
        return [serialize_object(obj) for obj in doc.Objects] if doc else []

    def get_object(self, doc_name: str, obj_name: str):
        """
        Gets a single serialized object from the document.

        Args:
            doc_name: Document name.
            obj_name: Object name to retrieve.

        Returns:
            Serialized object dictionary or None.
        """
        doc = App.getDocument(doc_name)
        return serialize_object(doc.getObject(obj_name)) if doc else None

    def get_active_screenshot(self, view_name: str = "Isometric"):
        """
        Captures a screenshot from the current active view in FreeCAD.

        Args:
            view_name: One of the view presets (e.g., Isometric, Top, Front).

        Returns:
            Base64-encoded PNG image string.
        """
        def task():
            if not Gui.ActiveDocument:
                return None
            view = Gui.ActiveDocument.ActiveView
            getattr(view, f"view{view_name.capitalize()}")()
            view.fitAll()
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            view.saveImage(tmp.name, 1)
            return tmp.name
        path = self.proxy.run(task)
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        os.remove(path)
        return encoded

    def execute_code(self, code: str):
        """
        Executes raw Python code inside FreeCAD GUI context (sandboxed).

        Args:
            code: String of Python code.

        Returns:
            Dict with success, output or traceback info.
        """
        import io, contextlib
        output = io.StringIO()
        def task():
            try:
                with contextlib.redirect_stdout(output):
                    exec(code, globals())
                return {"success": True, "output": output.getvalue()}
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                return {"success": False, "error": str(e), "traceback": tb}
        return self.proxy.run(task)

    def run_cnc_manufacturing_dfm_check(self, doc: str, params_json: str):
        """
        Runs a CNC Design for Manufacturing (DFM) analysis on the specified document.

        Args:
            doc (str): Name of the FreeCAD document.
            params_json (str): JSON string with optional override parameters.
                Supported keys (all optional):
                {
                "min_wall_thickness": float,         # Minimum wall thickness (default 1.0 mm)
                "max_aspect_ratio": float,           # Maximum height-to-width ratio (default 4.0)
                "min_radius": float,                 # Minimum corner radius (default 1.0 mm)
                "min_internal_corner_radius": float  # Minimum inner fillet radius (default 0.5 mm)
                }

        Returns:
            dict: {
                "success": bool,
                "issues": list[dict]  # List of issue descriptions and affected geometry
            }
        """
        params = json.loads(params_json)
        args = {
            "min_radius": 1.0,
            "max_aspect_ratio": 4.0,
            "min_internal_corner_radius": 0.5,
            "min_wall_thickness": 1.0
        } | params
        return self._run_dfm_check(doc, run_cnc_dfm_checker, args)

    def run_3d_printing_dfm_check(self, doc: str, params_json: str):
        """
        Checks the document for common 3D printing issues.

        Args:
            doc (str): The document name.
            params_json (str): Optional overrides:
                {
                    "process_type": str,
                    "min_wall_thickness": float,
                    "min_feature_size": float,
                    "max_overhang_angle": float,
                    "min_hole_radius": float,
                    "min_clearance": float,
                    "max_aspect_ratio": float
                }

        Returns:
            dict: {
                "success": bool,
                "issues": list[dict]
            }
        """
        params = json.loads(params_json)
        args = {
            "process_type": "Other",
            "min_wall_thickness": 1.0,
            "min_feature_size": 0.8,
            "max_overhang_angle": 45.0,
            "min_hole_radius": 2.0,
            "min_clearance": 0.5,
            "max_aspect_ratio": 20
        } | params
        return self._run_dfm_check(doc, run_tdp_dfm_checker, args)

    def run_injection_molding_dfm_check(self, doc: str, params_json: str):
        """
        Checks if the design meets standard injection molding guidelines.

        Args:
            doc (str): The document name.
            params_json (str): Optional rule overrides:
                {
                    "min_wall_thickness": float,
                    "max_wall_thickness": float,
                    "min_draft_angle": float,
                    "min_internal_corner_radius": float,
                    "max_aspect_ratio": float
                }

        Returns:
            dict: {
                "success": bool,
                "issues": list[dict]
            }
        """
        params = json.loads(params_json)
        args = {
            "min_wall_thickness": 0.5,
            "max_wall_thickness": 4.0,
            "min_draft_angle": 0.5,
            "min_internal_corner_radius": 0.25,
            "max_aspect_ratio": 5.0
        } | params
        return self._run_dfm_check(doc, run_im_dfm_checker, args)

    def restore_colors_after_check(self, doc_name: str):
        def restore():
            messages = []
            if doc_name in self.colors_storage:
                colors = self.colors_storage.pop(doc_name)
                messages.append(restore_original_colors(doc_name, colors))
            if doc_name in self.additional_objects:
                extras = self.additional_objects.pop(doc_name)
                messages.append(remove_additional_objects(doc_name, extras))
            return " ".join(messages).strip()
        msg = self.proxy.run(restore)
        return {"success": not msg, "message": msg}

    def _run_dfm_check(self, doc: str, checker_func, args: dict):
        def task():
            return checker_func(doc, **args)
        res = self.proxy.run(task)
        success, issues, _, checker = res
        if checker:
            self.colors_storage[doc] = getattr(checker, "original_colors", {})
            self.additional_objects[doc] = getattr(checker, "additional_objects", {})
        return {"success": success, "issues": issues}

    def get_cnc_dfm_rules(self):
        """
        Gets a dictionary of CNC manufacturability rules/features.

        Returns:
            dict: {
                "Feature": [{"Name": str, "Description": str}, ...]
            }
        """
        return get_cnc_machining_guidelines({
            "Feature": [
                {"Name": f, "Description": d}
                for f, d in zip(
                    self.dfm_cnc_rules_df["Feature"].unique(),
                    self.dfm_cnc_rules_df["Description"].unique()
                )
            ]
        })

    def get_3d_printing_dfm_rules(self):
        """
        Gets a dictionary of 3D printing design rules grouped by process.

        Returns:
            dict: {
                "Feature": [{"Name": str, "Description": str}],
                "Process": list[str]
            }
        """
        return get_3d_printing_guidelines({
            "Feature": [
                {"Name": f, "Description": d}
                for f, d in zip(
                    self.dfm_3d_rules_df["Feature"].dropna().unique(),
                    self.dfm_3d_rules_df["Description"].dropna().unique()
                )
            ],
            "Process": self.dfm_3d_rules_df["Process"].unique().tolist()
        })

    def get_cnc_dfm_rules(self):
        """
        Gets a dictionary of rules for injection molding design checks.

        Returns:
            dict: {
                "Feature": [{"Name": str, "Description": str}]
            }
        """
        return get_cnc_machining_guidelines({
            "Feature": [
                {"Name": f, "Description": d}
                for f, d in zip(
                    self.dfm_cnc_rules_df["Feature"].unique(),
                    self.dfm_cnc_rules_df["Description"].unique()
                )
            ]
        })

    def get_injection_molding_dfm_rules(self):
        return get_injection_molding_guidelines({
            "Feature": [
                {"Name": f, "Description": d}
                for f, d in zip(
                    self.dfm_im_rules_df["Feature"].unique(),
                    self.dfm_im_rules_df["Description"].unique()
                )
            ]
        })

    def _create_object_gui(self, doc_name: str, obj: Object) -> bool:
        doc = App.getDocument(doc_name)
        if doc:
            try:
                if obj.type == "Fem::FemMeshGmsh" and obj.analysis:
                    from femmesh.gmshtools import GmshTools
                    import ObjectsFem
                    res = getattr(doc, obj.analysis).addObject(ObjectsFem.makeMeshGmsh(doc, obj.name))[0]
                    if "Part" in obj.properties:
                        target_obj = doc.getObject(obj.properties["Part"])
                        if target_obj:
                            res.Part = target_obj
                        else:
                            raise ValueError(f"Referenced object '{obj.properties['Part']}' not found.")
                        del obj.properties["Part"]
                    else:
                        raise ValueError("'Part' property not found in properties.")

                    for param, value in obj.properties.items():
                        if hasattr(res, param):
                            setattr(res, param, value)
                    doc.recompute()

                    gmsh_tools = GmshTools(res)
                    gmsh_tools.create_mesh()
                    App.Console.PrintMessage(
                        f"FEM Mesh '{res.Name}' generated successfully in '{doc_name}'.\n"
                    )
                elif obj.type.startswith("Fem::"):
                    fem_make_methods = {
                        "MaterialCommon": ObjectsFem.makeMaterialSolid,
                        "AnalysisPython": ObjectsFem.makeAnalysis,
                    }
                    obj_type_short = obj.type.split("::")[1]
                    method_name = "make" + obj_type_short
                    make_method = fem_make_methods.get(obj_type_short, getattr(ObjectsFem, method_name, None))

                    if callable(make_method):
                        res = make_method(doc, obj.name)
                        self._set_object_property(doc, res, obj.properties)
                        App.Console.PrintMessage(
                            f"FEM object '{res.Name}' created with '{method_name}'.\n"
                        )
                    else:
                        raise ValueError(f"No creation method '{method_name}' found in ObjectsFem.")
                    if obj.type != "Fem::AnalysisPython" and obj.analysis:
                        getattr(doc, obj.analysis).addObject(res)
                else:
                    res = doc.addObject(obj.type, obj.name)
                    self._set_object_property(doc, res, obj.properties)
                    App.Console.PrintMessage(
                        f"{res.TypeId} '{res.Name}' added to '{doc_name}' via RPC.\n"
                    )
 
                doc.recompute()
                return True
            except Exception as e:
                return str(e)
        else:
            App.Console.PrintError(f"Document '{doc_name}' not found.\n")
            return False

    def _edit_object_gui(self, doc_name: str, obj: Object) -> bool:
        doc = App.getDocument(doc_name)
        if not doc:
            App.Console.PrintError(f"Document '{doc_name}' not found.\n")
            return False

        obj_ins = doc.getObject(obj.name)
        if not obj_ins:
            App.Console.PrintError(f"Object '{obj.name}' not found in document '{doc_name}'.\n")
            return False

        try:
            # For Fem::ConstraintFixed
            if hasattr(obj_ins, "References") and "References" in obj.properties:
                refs = []
                for ref_name, face in obj.properties["References"]:
                    ref_obj = doc.getObject(ref_name)
                    if ref_obj:
                        refs.append((ref_obj, face))
                    else:
                        raise ValueError(f"Referenced object '{ref_name}' not found.")
                obj_ins.References = refs
                App.Console.PrintMessage(
                    f"References updated for '{obj.name}' in '{doc_name}'.\n"
                )
                # delete References from properties
                del obj.properties["References"]
            self._set_object_property(doc, obj_ins, obj.properties)
            doc.recompute()
            App.Console.PrintMessage(f"Object '{obj.name}' updated via RPC.\n")
            return True
        except Exception as e:
            return str(e)

    def _delete_object_gui(self, doc_name: str, obj_name: str) -> bool:
        doc = App.getDocument(doc_name)
        if not doc:
            App.Console.PrintError(f"Document '{doc_name}' not found.\n")
            return False

        try:
            doc.removeObject(obj_name)
            doc.recompute()
            App.Console.PrintMessage(f"Object '{obj_name}' deleted via RPC.\n")
            return True
        except Exception as e:
            return str(e)

    @staticmethod
    def _set_object_property(doc: App.Document, obj: App.DocumentObject, properties: dict[str, Any]):
        for prop, val in properties.items():
            try:
                if prop in obj.PropertiesList:
                    if prop == "Placement" and isinstance(val, dict):
                        if "Base" in val:
                            pos = val["Base"]
                        elif "Position" in val:
                            pos = val["Position"]
                        else:
                            pos = {}
                        rot = val.get("Rotation", {})
                        placement = App.Placement(
                            App.Vector(
                                pos.get("x", 0),
                                pos.get("y", 0),
                                pos.get("z", 0),
                            ),
                            App.Rotation(
                                App.Vector(
                                    rot.get("Axis", {}).get("x", 0),
                                    rot.get("Axis", {}).get("y", 0),
                                    rot.get("Axis", {}).get("z", 1),
                                ),
                                rot.get("Angle", 0),
                            ),
                        )
                        setattr(obj, prop, placement)

                    elif isinstance(getattr(obj, prop), App.Vector) and isinstance(
                        val, dict
                    ):
                        vector = App.Vector(
                            val.get("x", 0), val.get("y", 0), val.get("z", 0)
                        )
                        setattr(obj, prop, vector)

                    elif prop in ["Base", "Tool", "Source", "Profile"] and isinstance(
                        val, str
                    ):
                        ref_obj = doc.getObject(val)
                        if ref_obj:
                            setattr(obj, prop, ref_obj)
                        else:
                            raise ValueError(f"Referenced object '{val}' not found.")

                    elif prop == "References" and isinstance(val, list):
                        refs = []
                        for ref_name, face in val:
                            ref_obj = doc.getObject(ref_name)
                            if ref_obj:
                                refs.append((ref_obj, face))
                            else:
                                raise ValueError(f"Referenced object '{ref_name}' not found.")
                        setattr(obj, prop, refs)

                    else:
                        setattr(obj, prop, val)
                # ShapeColor is a property of the ViewObject
                elif prop == "ShapeColor" and isinstance(val, (list, tuple)):
                    setattr(obj.ViewObject, prop, (float(val[0]), float(val[1]), float(val[2]), float(val[3])))

                elif prop == "ViewObject" and isinstance(val, dict):
                    for k, v in val.items():
                        if k == "ShapeColor":
                            setattr(obj.ViewObject, k, (float(v[0]), float(v[1]), float(v[2]), float(v[3])))
                        else:
                            setattr(obj.ViewObject, k, v)

                else:
                    setattr(obj, prop, val)

            except Exception as e:
                App.Console.PrintError(f"Property '{prop}' assignment error: {e}\n")
