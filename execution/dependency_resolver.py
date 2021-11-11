
from network.network import ReceiverQueue
from execution.operations import Operation
from queue import Queue
from threading import Thread

from util.logger import Logger


class DoneOperationsQueue:
    # simple hashset to check if operation ids are already executed

    def __init__(self):
        self.q = set()

    def insert(self, operation: Operation):
        self.q.add(str(operation.id))

    # given a operation check if all its dependencies are already executed i.e. present in done queue
    def check_depencecies(self, operation: Operation):
        for dependency in operation.dependecies:
            if not str(dependency) in self.q:
                return False
        return True


class ExecutionQueue:
    # simple thread safe queue to buffer remote operations ready for execution

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
    # resolve dependencies for remote ops
    # transfer ops from recv queue to executioin queue if depencencies are resolved
    # asynchronous polling

    def __init__(self, execution_queue: ExecutionQueue, done_operations_queue: DoneOperationsQueue, recv_queue: ReceiverQueue):
        self.exq = execution_queue
        self.doq = done_operations_queue
        self.rcq = recv_queue
        self.log = Logger()

    def _start(self):
        while True:
            op = self.rcq.pop()
            if op:
                if self.doq.check_depencecies(op):
                    self.log.info("dependencies_resolved: ", op)
                    self.exq.push(op)
                else:
                    self.rcq.push(op)

    def start(self):
        t = Thread(target=self._start)
        t.start()
