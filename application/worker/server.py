import logging
from zmq import green as zmq
from agentzero.core import SocketManager
from application.worker.config import DEFAULT_DEALER_ADDRESS

context = zmq.Context()

logger = logging.getLogger("server")


class EchoServer(object):
    def __init__(self, zmq_uri=DEFAULT_DEALER_ADDRESS):

        self.sockets = SocketManager(zmq, context)
        self.sockets.ensure_and_connect(
            "responder", zmq.REP, zmq_uri, zmq.POLLIN | zmq.POLLOUT,
            polling_timeout=500,
            timeout=1,
        )
        self.should_run = True
        self.zmq_uri = zmq_uri
        logger.info(f"Initializing ZMQ Response Server: {self.zmq_uri!r}")

    def run(self):
        logger.info(f"Starting {self} in {self.zmq_uri}")
        while self.should_run:
            request = self.sockets.recv_safe("responder")

            if not request:
                logger.info("ready for request")
                continue

            self.should_run = request != "close"
            logger.info(f'received request {request!r}')
            print(f'\033[1;32m{request!r}\033[0m')
            # logger.info(f'request: {request!r}')

            if not self.should_run:
                logger.warning('shutting-down because of client "close"')

            response = request
            if self.sockets.send_safe("responder", response):
                logger.info(f"echo: {response!r}")

        logger.warning('shutting down server')
