import gevent.monkey


import gevent
import coloredlogs
import logging
from zmq import green as zmq
from agentzero.core import SocketManager

context = zmq.Context()
coloredlogs.install(level='DEBUG')

logger = logging.getLogger('server')


class EchoServer(object):
    def __init__(self):
        self.sockets = SocketManager(zmq, context)
        self.sockets.ensure_and_bind(
             "responder",
             zmq.REP,
             'tcp://127.0.0.1:5051',
             zmq.POLLIN | zmq.POLLOUT
        )
        self.should_run = True

    def run(self):
        while self.should_run:
            request = self.sockets.recv_safe('responder')

            if not request:
                logger.info('waiting')
                continue

            self.should_run = request != 'close'
            # logger.info(f'request: {request!r}')

            response = request
            if self.sockets.send_safe('responder', response):
                logger.info(f'echo: {response!r}')


if __name__ == '__main__':
    gevent.monkey.patch_all()
    logger.info('init')
    EchoServer().run()
