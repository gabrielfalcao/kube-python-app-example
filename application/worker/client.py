
import logging
from zmq import green as zmq
from agentzero.core import SocketManager
from application.worker.config import DEFAULT_ROUTER_ADDRESS

context = zmq.Context()


logger = logging.getLogger('server')


class EchoClient(object):
    def __init__(self, zmq_uri=DEFAULT_ROUTER_ADDRESS):
        self.sockets = SocketManager(zmq, context)
        self.sockets.ensure_and_connect(
             "requester",
             zmq.REQ,
             zmq_uri,
             zmq.POLLIN | zmq.POLLOUT
        )
        self.should_run = True
        self.zmq_uri = zmq_uri
        logger.info(f'Initializing ZMQ Request Client: {self.zmq_uri!r}')

    def request(self, data):
        logger.info(f'request: {data}')
        self.sockets.send_safe('requester', data)
        response = self.sockets.recv_safe('requester')
        logger.info(f'response: {response}')
        return response
