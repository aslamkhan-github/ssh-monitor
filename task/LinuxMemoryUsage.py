import logging
import socket

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class LinuxMemoryUsage:

    def __init__(self, host, port, session, path):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.destination = (host, port)
        self.session = session
        self.path = path

    def on_output(self, task, line):
        out = line.split()
        msg = '{}:{}|g\n'.format(self.path + '.memory.free', out[-1])
        msg += '{}:{}|g'.format(self.path + '.memory.used', out[-2])
        # self.sock.sendto(msg, self.destination)
        logger.info('Sent:\n%s', msg)

    def execute(self):
        self.session.execute('free -m | grep +', on_stdout=self.on_output)
