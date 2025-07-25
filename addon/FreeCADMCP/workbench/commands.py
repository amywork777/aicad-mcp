import FreeCADGui as Gui
from dfm.cnc_check12 import CNCDFMCheckerDialog
from dfm.tdp_check3 import TDPDFMCheckerDialog
from dfm.injectm_check3 import InjectionMoldingDFMCheckerDialog

import FreeCAD as App
from PySide2 import QtGui


def validate_document() -> bool:
    doc = App.activeDocument()
    if doc is None:
        QtGui.QMessageBox.critical(None, "DFM Error", "No document, open or create one.")
        return False
    if not doc.Objects:
        QtGui.QMessageBox.critical(None, "DFM Error", "Document is empty, add objects first.")
        return False
    return True

class DFMCommand:
    def __init__(self, dialog_class, label: str, tooltip: str):
        self.dialog_class = dialog_class
        self.label = label
        self.tooltip = tooltip

    def GetResources(self):
        return {
            "MenuText": self.label,
            "ToolTip": self.tooltip,
            "Pixmap": ""
        }

    def IsActive(self):
        return True

    def Activated(self):
        if not validate_document():
            return
        dlg = self.dialog_class()
        dlg.show()

commands = {
    "CNC_Manufacturing_Analyze": {
        "dialog": CNCDFMCheckerDialog,
        "label": "Analyze CNC Manufacturing",
        "tooltip": "Analyse model for CNC Manufacturing conditions"
    },
    "3D_Printing_Analyze": {
        "dialog": TDPDFMCheckerDialog,
        "label": "Analyze 3D Printing",
        "tooltip": "Analyse model for 3D Printing conditions"
    },
    "Inject_Molding_Analyze": {
        "dialog": InjectionMoldingDFMCheckerDialog,
        "label": "Analyze Injection Molding",
        "tooltip": "Analyse model for Injection Molding conditions"
    }
}

def register_commands():
    for name, cfg in commands.items():
        Gui.addCommand(name, DFMCommand(cfg["dialog"], cfg["label"], cfg["tooltip"]))

register_commands.commands = commands