from util.logger import Logger
from flask import Flask, request
from flask.wrappers import Request
from execution.dependency_resolver import DependencyResolver, DoneOperationsQueue, ExecutionQueue

from execution.operations import Operation, OperationType
from lamport.lamport import LamportCounter
from network.network import ReceiverQueue, SenderQueue
from store.json_store import Store
from store.serializer import deserialize, serialize

api = Flask(__name__)


class RequestHandler:
    def __init__(self):
        self.counter = LamportCounter()
        self.done_queue = DoneOperationsQueue()
        self.execution_queue = ExecutionQueue()
        self.send_queue = SenderQueue()
        self.recv_queue = ReceiverQueue()
        self.dependency_resolver = DependencyResolver(
            self.execution_queue, self.done_queue, self.recv_queue)
        self.state = Store()
        self.log = Logger()

        self.dependency_resolver.start()
        self.send_queue.start()

    def _execute(self, op: Operation):
        # maxi lamport counter
        self.counter.set(max(self.counter.counter, op.id.counter))
        self.done_queue.insert(op)
        print("OPERATION: ", op)
        res = self.state.execute(op)
        print("STATE: ", self.state)
        return serialize(res)

    def execute(self, op: Operation):
        # process remote execution queue
        remote_op = self.execution_queue.pop()
        while remote_op:
            self._execute(remote_op)
            remote_op = self.execution_queue.pop()

        return self._execute(op)

    def process_remote(self, req: Request):
        op = deserialize(req.json)
        self.recv_queue.push(op)
        return serialize(None)

    def process_local(self, req: Request):
        req_type = OperationType.GET
        if req.json["type"] == "delete":
            req_type = OperationType.DELETE
        elif req.json["type"] == "insert":
            req_type = OperationType.INSERT
        elif req.json["type"] == "assign":
            req_type = OperationType.ASSIGN

        if req_type != OperationType.GET:
            self.counter.increment()
        payload = None
        if req_type in [OperationType.INSERT, OperationType.ASSIGN]:
            payload = deserialize(req.json["payload"])
            payload.last_modified = self.counter.get()
        args = None
        if req_type == OperationType.INSERT:
            args = req.json["args"]
        op = Operation(self.counter.get(), [], req.json["cursor"],
                       False, req_type, payload, args)

        # generate remote op
        deps = []
        if len(self.done_queue.q):
            deps = [max(self.done_queue.q)]
        remote_op = Operation(
            op.id, deps, op.cursor, True, op.type, op.payload, op.args)
        self.send_queue.push(remote_op)

        # execute
        return self.execute(op)


handler = RequestHandler()


@api.route('/', methods=['POST'])
def post_client():
    return handler.process_local(request), 200


@api.route('/replicate', methods=['POST'])
def post_replica():
    return handler.process_remote(request), 200


if __name__ == '__main__':
    api.run(threaded=False, debug=True)
