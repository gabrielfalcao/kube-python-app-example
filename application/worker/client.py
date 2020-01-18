import os
import uuid
import gevent.monkey


import gevent
import coloredlogs
import logging
from zmq import green as zmq
from agentzero.core import SocketManager
from names import generate_name
context = zmq.Context()
coloredlogs.install(level='DEBUG')

logger = logging.getLogger('server')


class EchoClient(object):
    def __init__(self):
        self.sockets = SocketManager(zmq, context)
        self.sockets.ensure_and_connect(
             "requester",
             zmq.REQ,
             'tcp://127.0.0.1:5051',
             zmq.POLLIN | zmq.POLLOUT
        )
        self.should_run = True

    def request(self, data):
        logger.info(f'request: {data}')
        if self.sockets.send_safe('requester', data):
            response = self.sockets.recv_safe('requester')
            logger.info(f'response: {response}')


if __name__ == '__main__':
    gevent.monkey.patch_all()
    PID = os.getpid()
    try:
        while True:
            EchoClient().request(f'{PID}\t{generate_name()}')
            gevent.sleep(0.3)
    except KeyboardInterrupt:
        raise SystemExit(1)
