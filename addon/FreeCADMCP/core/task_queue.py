import queue
from PySide2.QtCore import QTimer

rpc_request_queue = queue.Queue()
rpc_response_queue = queue.Queue()

def process_gui_tasks():
    while not rpc_request_queue.empty():
        task = rpc_request_queue.get()
        res = task()
        if res is not None:
            rpc_response_queue.put(res)
    QTimer.singleShot(500, process_gui_tasks)