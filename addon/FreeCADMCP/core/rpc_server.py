from xmlrpc.server import SimpleXMLRPCServer
from PySide2.QtCore import QTimer
from .task_queue import process_gui_tasks

rpc_server_instance = None
rpc_server_thread = None

def start_rpc_server(host="localhost", port=9875):
    global rpc_server_instance, rpc_server_thread
    if rpc_server_instance:
        return "RPC Server already running."

    from threading import Thread
    from .rpc_handler import FreeCADRPC

    rpc_server_instance = SimpleXMLRPCServer((host, port), allow_none=True, logRequests=False)
    rpc_server_instance.register_instance(FreeCADRPC())

    def server_loop():
        import FreeCAD
        FreeCAD.Console.PrintMessage(f"RPC Server started at {host}:{port}\n")
        rpc_server_instance.serve_forever()

    rpc_server_thread = Thread(target=server_loop, daemon=True)
    rpc_server_thread.start()
    QTimer.singleShot(500, process_gui_tasks)

    return f"RPC Server started at {host}:{port}."

def stop_rpc_server():
    global rpc_server_instance, rpc_server_thread
    if rpc_server_instance:
        rpc_server_instance.shutdown()
        rpc_server_thread.join()
        rpc_server_instance = None
        rpc_server_thread = None
        return "RPC Server stopped."
    return "RPC Server was not running."