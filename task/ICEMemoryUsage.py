import logging
import pickle
import struct
import time

import traceback
from SShUtil import CreateSshSession, SendGraphitePayload

# logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ICEMemoryUsage:

    def __init__(self, task):
        self.destination = (task.db_host, task.db_port)
        self.task = task

    def on_output(self, task, line):
        now = int(time.time())
        out = line.split()

        try:
            used = int(out[1]) - int(out[-1])
            free = (self.task.path + '.memory.free', (now, out[-1]))
            used = (self.task.path + '.memory.used', (now, used))
            total = (self.task.path + '.memory.total', (now, out[1]))

            payload = pickle.dumps([free, used, total], protocol=2)
            header = struct.pack("!L", len(payload))

            if SendGraphitePayload(self.destination, header, payload):
                logger.debug('Sent:\n%s', [free, used, total])

        except:
            logger.error(traceback.format_exc)

    def on_swap_output(self, tak, line):
        now = int(time.time())
        out = line.split()

        try:
            free = (self.task.path + '.memory.swap_free', (now, out[-1]))
            used = (self.task.path + '.memory.swap_used', (now, out[-2]))
            total = (self.task.path + '.memory.swap_total', (now, out[-3]))

            payload = pickle.dumps([free, used, total], protocol=2)
            header = struct.pack("!L", len(payload))

            if SendGraphitePayload(self.destination, header, payload):
                logger.debug('Sent:\n%s', [free, used, total])

        except:
            logger.error(traceback.format_exc)

    def execute(self):
        session = CreateSshSession(self.task)
        if not session:
            return
        session.execute('free -m | grep Mem', on_stdout=self.on_output)
        session.execute('free -m | grep Swap',
                        on_stdout=self.on_swap_output)
