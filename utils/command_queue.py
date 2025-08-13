from collections import defaultdict, deque
import threading

# Thread-safe command queue implementation
class CommandQueue:
    def __init__(self):
        self.queues = defaultdict(deque)
        self.lock = threading.Lock()

    def put(self, client_id, command):
        with self.lock:
            self.queues[client_id].append(command)

    def get(self, client_id):
        with self.lock:
            if self.queues[client_id]:
                return self.queues[client_id].popleft()
            return None

    def is_empty(self, client_id):
        with self.lock:
            return not bool(self.queues[client_id])

# Usage
COMMAND_QUEUE = CommandQueue()
