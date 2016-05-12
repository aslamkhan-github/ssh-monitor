import logging
import pickle
import struct
import time

from SShUtil import CreateSshSession, SendGraphitePayload

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ICEMemoryUsage:

    def __init__(self, task):
        self.destination = (task.db_host, task.db_port)
        self.session = CreateSshSession(task)
        self.path = task.path

    def on_output(self, task, line):
        now = int(time.time())
        out = line.split()

        used = int(out[1]) - int(out[-1])
        free = (self.path + '.memory.free', (now, out[-1]))
        used = (self.path + '.memory.used', (now, used))
        total = (self.path + '.memory.used', (now, out[1]))

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

    '''

    def on_output(self, task, line):
        out = line.split()
        msg = '{}:{}|c\n'.format(self.path + '.memory.free', out[-1])
        used = int(out[1]) - int(out[-1])
        msg += '{}:{}|c\n'.format(self.path + '.memory.used', used)
        msg += '{}:{}|c'.format(self.path + '.memory.total', out[1])
        self.sock.sendto(msg, self.destination)
        logger.info('Sent:\n%s', msg)

    def on_swap_output(self, tak, line):
        out = line.split()
        msg = '{}:{}|c\n'.format(self.path + '.memory.swap_free', out[-1])
        msg += '{}:{}|c\n'.format(self.path + '.memory.swap_used', out[-2])
        msg += '{}:{}|c'.format(self.path + '.memory.swap_total', out[-3])
        self.sock.sendto(msg, self.destination)
        logger.info('Sent:\n%s', msg)
    '''

    def execute(self):
        self.session.execute('free -m | grep Mem', on_stdout=self.on_output)
        self.session.execute('free -m | grep Swap',
                             on_stdout=self.on_swap_output)
