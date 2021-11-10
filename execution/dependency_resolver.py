
from network.network import ReceiverQueue
from execution.operations import Operation
from queue import Queue
from threading import Thread


class DoneOperationsQueue:
    def __init__(self):
        self.q = set()

    def insert(self, operation: Operation):
        self.q.add(operation.id)

    def check_depencecies(self, operation: Operation):
        for dependency in operation.dependecies:
            if dependency not in self.q:
                return False
        return True


class ExecutionQueue:
    def __init__(self):
        self.q = Queue()

    def push(self, operation: Operation):
        self.q.put(operation)

    def pop(self):
        if self.q.empty():
            return None
        else:
            return self.q.get()


class DependencyResolver:
    def __init__(self, execution_queue: ExecutionQueue, done_operations_queue: DoneOperationsQueue, recv_queue: ReceiverQueue):
        self.exq = execution_queue
        self.doq = done_operations_queue
        self.rcq = recv_queue

    def _start(self):
        while True:
            op = self.rcq.pop()
            if op:
                if self.doq.check_depencecies(op):
                    self.exq.push(op)
                else:
                    self.rcq.push(op)

    def start(self):
        t = Thread(target=self._start)
        t.start()
