from .task_queue import rpc_request_queue, rpc_response_queue

class RPCProxy:
    def __init__(self):
        self.queue = rpc_request_queue
        self.response = rpc_response_queue

    def run(self, func):
        self.queue.put(func)
        return self.response.get()