# Auto-generated OpenAI tool schemas from FreeCADRPC methods

tool_schemas = [
    {
        "type": "function",
        "function": {
            "name": "ping",
            "description": "Simple health check to verify the RPC service is responsive.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_documents",
            "description": "Returns a list of all currently open FreeCAD document names.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_document",
            "description": "Creates a new FreeCAD document with the given name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "name parameter"
                    }
                },
                "required": [
                    "name"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_object",
            "description": "Creates a new FreeCAD object in the specified document using JSON parameters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_name": {
                        "type": "string",
                        "description": "Name of the target FreeCAD document. (type: str)"
                    },
                    "params_json": {
                        "type": "string",
                        "description": "JSON string with the following structure: (type: str) { \"Name\": str,              # Object name \"Type\": str,              # FreeCAD type (e.g., \"Part::Box\", \"Fem::ConstraintFixed\") \"Analysis\": Optional[str],# FEM analysis to associate with, if applicable \"Properties\": dict        # Key-value pairs for object properties }  Example: { \"Name\": \"MyBox\", \"Type\": \"Part::Box\", \"Properties\": { \"Length\": 10.0, \"Width\": 10.0, \"Height\": 5.0, \"ShapeColor\": [0.3, 0.4, 0.9, 1.0], \"Placement\": { \"Base\": {\"x\": 0, \"y\": 0, \"z\": 0}, \"Rotation\": { \"Axis\": {\"x\": 0, \"y\": 0, \"z\": 1}, \"Angle\": 45 } } } }"
                    }
                },
                "required": [
                    "doc_name",
                    "params_json"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_object",
            "description": "Edits an existing FreeCAD object by updating its properties.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_name": {
                        "type": "string",
                        "description": "The document where the object is located. (type: str)"
                    },
                    "obj_name": {
                        "type": "string",
                        "description": "The name of the object to be modified. (type: str)"
                    },
                    "params_json": {
                        "type": "string",
                        "description": "JSON string of properties to update. (type: str) This JSON should be of the form: { \"Length\": 15.0, \"ShapeColor\": [1.0, 0.0, 0.0, 1.0], \"Placement\": { \"Base\": {\"x\": 5, \"y\": 0, \"z\": 0}, \"Rotation\": { \"Axis\": {\"x\": 0, \"y\": 1, \"z\": 0}, \"Angle\": 90 } } }"
                    }
                },
                "required": [
                    "doc_name",
                    "obj_name",
                    "params_json"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_object",
            "description": "Deletes an object from the specified document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_name": {
                        "type": "string",
                        "description": "doc_name parameter"
                    },
                    "obj_name": {
                        "type": "string",
                        "description": "obj_name parameter"
                    }
                },
                "required": [
                    "doc_name",
                    "obj_name"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "export_step",
            "description": "Exports all valid shapes in a document to a single STEP file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_name": {
                        "type": "string",
                        "description": "doc_name parameter"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "file_path parameter"
                    }
                },
                "required": [
                    "doc_name",
                    "file_path"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "insert_part_from_library",
            "description": "Inserts a part from a predefined library into the active document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "relative_path": {
                        "type": "string",
                        "description": "relative_path parameter"
                    }
                },
                "required": [
                    "relative_path"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_parts_list",
            "description": "Retrieves a list of available parts from the internal part library.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_objects",
            "description": "Returns serialized data for all objects in a given document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_name": {
                        "type": "string",
                        "description": "doc_name parameter"
                    }
                },
                "required": [
                    "doc_name"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_object",
            "description": "Gets a single serialized object from the document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_name": {
                        "type": "string",
                        "description": "doc_name parameter"
                    },
                    "obj_name": {
                        "type": "string",
                        "description": "obj_name parameter"
                    }
                },
                "required": [
                    "doc_name",
                    "obj_name"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_active_screenshot",
            "description": "Captures a screenshot from the current active view in FreeCAD.",
            "parameters": {
                "type": "object",
                "properties": {
                    "view_name": {
                        "type": "string",
                        "description": "view_name parameter"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": "Executes raw Python code inside FreeCAD GUI context (sandboxed).",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "code parameter"
                    }
                },
                "required": [
                    "code"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_cnc_manufacturing_dfm_check",
            "description": "Runs a CNC Design for Manufacturing (DFM) analysis on the specified document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc": {
                        "type": "string",
                        "description": "Name of the FreeCAD document. (type: str)"
                    },
                    "params_json": {
                        "type": "string",
                        "description": "JSON string with optional override parameters. (type: str) Supported keys (all optional): { \"min_wall_thickness\": float,         # Minimum wall thickness (default 1.0 mm) \"max_aspect_ratio\": float,           # Maximum height-to-width ratio (default 4.0) \"min_radius\": float,                 # Minimum corner radius (default 1.0 mm) \"min_internal_corner_radius\": float  # Minimum inner fillet radius (default 0.5 mm) }"
                    }
                },
                "required": [
                    "doc",
                    "params_json"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_3d_printing_dfm_check",
            "description": "Checks the document for common 3D printing issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc": {
                        "type": "string",
                        "description": "The document name. (type: str)"
                    },
                    "params_json": {
                        "type": "string",
                        "description": "Optional overrides: (type: str) { \"process_type\": str, \"min_wall_thickness\": float, \"min_feature_size\": float, \"max_overhang_angle\": float, \"min_hole_radius\": float, \"min_clearance\": float, \"max_aspect_ratio\": float }"
                    }
                },
                "required": [
                    "doc",
                    "params_json"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_injection_molding_dfm_check",
            "description": "Checks if the design meets standard injection molding guidelines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc": {
                        "type": "string",
                        "description": "The document name. (type: str)"
                    },
                    "params_json": {
                        "type": "string",
                        "description": "Optional rule overrides: (type: str) { \"min_wall_thickness\": float, \"max_wall_thickness\": float, \"min_draft_angle\": float, \"min_internal_corner_radius\": float, \"max_aspect_ratio\": float }"
                    }
                },
                "required": [
                    "doc",
                    "params_json"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "restore_colors_after_check",
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_name": {
                        "type": "string",
                        "description": "doc_name parameter"
                    }
                },
                "required": [
                    "doc_name"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cnc_dfm_rules",
            "description": "Gets a dictionary of CNC manufacturability rules/features.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_3d_printing_dfm_rules",
            "description": "Gets a dictionary of 3D printing design rules grouped by process.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_injection_molding_dfm_rules",
            "description": "Gets a dictionary of rules for injection molding design checks.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]