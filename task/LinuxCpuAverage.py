import logging
import socket

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class LinuxCpuAverage:

    def __init__(self, host, port, session, path):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.destination = (host, port)
        self.session = session
        self.path = path

    def on_output(self, task, line):
        out = line.split()
        msg = '{}:{}|c\n'.format(
            self.path + '.cpu_average.1min', out[-3].replace(',', ''))
        msg += '{}:{}|c\n'.format(self.path + '.cpu_average.5min',
                                  out[-2].replace(',', ''))
        msg += '{}:{}|c'.format(self.path + '.cpu_average.15min', out[-1])
        self.sock.sendto(msg, self.destination)
        logger.info('Sent:\n%s', msg)

    def execute(self):
        self.session.execute('uptime', on_stdout=self.on_output)
