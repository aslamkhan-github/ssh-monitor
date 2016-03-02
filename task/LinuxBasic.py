import socket
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinuxBasic:

    def __init__(self, host, port, session):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port
        self.n = 0

    def on_output(self, task, line):
        logger.info('%d - Received: %s', self.n, line)
        self.n += 1

    def execute(self):
        self.session.execute('uptime', on_stdout=self.on_output)
        self.session.execute('uptime', on_stdout=self.on_output)
