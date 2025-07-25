import FreeCAD
import FreeCADGui

class TaiyakiAIWorkbench(FreeCADGui.Workbench):
    MenuText = "Taiyaki AI"
    ToolTip = "DFM analysis and AI chat integration"
    Icon = ""

    def __init__(self):
        self._dock_widget = None
        self._rpc_thread = None

    def Initialize(self):
        # from workbench.commands import register_commands

        # register_commands()
        # self.appendToolbar("Taiyaki AI", list(register_commands.commands.keys()))
        # self.appendMenu("Taiyaki AI", list(register_commands.commands.keys()))
        pass

    def Activated(self):
        from core.rpc_server import start_rpc_server

        self._rpc_thread = start_rpc_server(host="localhost", port=9875)
        main_window = FreeCADGui.getMainWindow()
        if not main_window:
            return
        
        from PySide2 import QtCore, QtWidgets

        self._dock_widget = QtWidgets.QDockWidget("Chat", main_window)
        self._dock_widget.setObjectName("ChatWidget")

        from ui.widget import ChatWidget

        chat_widget = ChatWidget(parent=self._dock_widget)
        self._dock_widget.setWidget(chat_widget)
        main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self._dock_widget)
        self._dock_widget.show()

    def Deactivated(self):
        from core.rpc_server import stop_rpc_server

        stop_rpc_server()
        if self._dock_widget:
            main_window = FreeCADGui.getMainWindow()
            if main_window:
                main_window.removeDockWidget(self._dock_widget)
            self._dock_widget.setParent(None)
            self._dock_widget = None

    def GetClassName(self):
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(TaiyakiAIWorkbench())