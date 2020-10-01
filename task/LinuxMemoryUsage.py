import logging
import time
import pickle
import struct
import traceback
from datetime import datetime, timedelta
from SShUtil import CreateSshSession, SendGraphitePayload

# logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Physical Memory
class LinuxMemoryUsage:

    def __init__(self, task):
        self.destination = (task.db_host, task.db_port)
        self.task = task
        self.last_connection = None
        self.session = None

    def connect(self):
        # Check if already connected
        if self.session:
            # Expire session
            if datetime.now() - self.last_connection > timedelta(hours=1):
                self.session.close()
            else:
                # Keep session alive
                return True

        self.session = CreateSshSession(self.task)
        self.last_connection = datetime.now()
        return (self.session is not None)
     
    def on_output(self, task, line):
        now = int(time.time())
        out = line.split()

        try:
            total = int(out[-1]) + int(out[-2])
            free = (self.task.path + '.memory.free', (now, out[-1]))
            used = (self.task.path + '.memory.used', (now, out[-2]))
            total = (self.task.path + '.memory.total', (now, total))

            payload = pickle.dumps([free, used, total], protocol=2)
            header = struct.pack("!L", len(payload))

            if SendGraphitePayload(self.destination, header, payload):
                logger.debug('Sent:\n%s', [free, used, total])

        except:
            logger.error(traceback.format_exc)
    
    #SWAP MEMORY
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

    def execute(self, session=None):
        if session:
            # Use external session
            session.execute('free -m | grep +', on_stdout=self.on_output)
            session.execute('free -m | grep Swap',
                             on_stdout=self.on_swap_output)
        else:
            if not self.connect():
                return
            self.session.execute('free -m | grep +', on_stdout=self.on_output)
            self.session.execute('free -m | grep Swap',
                             on_stdout=self.on_swap_output)
