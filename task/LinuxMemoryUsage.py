import logging
import socket
import time
import pickle
import struct

from SShUtil import CreateSshSession, SendGraphitePayload

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class LinuxMemoryUsage:

    def __init__(self, task):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.destination = (task.db_host, task.db_port)
        self.session = CreateSshSession(task)
        self.path = task.path

    def on_output(self, task, line):
        now = int(time.time())
        out = line.split()

        total = int(out[-1]) + int(out[-2])
        free = (self.path + '.memory.free', (now, out[-1]))
        used = (self.path + '.memory.used', (now, out[-2]))
        total = (self.path + '.memory.total', (now, total))

        payload = pickle.dumps([free, used, total], protocol=2)
        header = struct.pack("!L", len(payload))

        if SendGraphitePayload(self.destination, header, payload):
            logger.info('Sent:\n%s', [free, used, total])

    def on_swap_output(self, tak, line):
        now = int(time.time())
        out = line.split()

        free = (self.path + '.memory.swap_free', (now, out[-1]))
        used = (self.path + '.memory.swap_used', (now, out[-2]))
        total = (self.path + '.memory.swap_total', (now, out[-3]))

        payload = pickle.dumps([free, used, total], protocol=2)
        header = struct.pack("!L", len(payload))

        if SendGraphitePayload(self.destination, header, payload):
            logger.info('Sent:\n%s', [free, used, total])

    def execute(self):
        self.session.execute('free -m | grep +', on_stdout=self.on_output)
        self.session.execute('free -m | grep Swap',
                             on_stdout=self.on_swap_output)
