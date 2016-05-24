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


class LinuxCpuAverage:

    def __init__(self, task):
        self.destination = (task.db_host, task.db_port)
        self.task = task
        self.session = None
        self.last_connection = None

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
        out = line.split()
        now = int(time.time())

        try:
            one = (self.task.path + '.cpu_average.1min',
                   (now, out[-3].replace(',', '')))
            five = (self.task.path + '.cpu_average.5min',
                    (now, out[-2].replace(',', '')))
            fiftheen = (self.task.path + '.cpu_average.15min',
                        (now, out[-1].replace(',', '')))

            package = [one, five, fiftheen]
            payload = pickle.dumps(package, protocol=2)
            header = struct.pack("!L", len(payload))

            if SendGraphitePayload(self.destination, header, payload):
                logger.debug('Sent:\n%s', package)

        except:
            logger.error(traceback.format_exc)

    def execute(self, session=None):
        if session:
            # use external session
            session.execute('uptime', on_stdout=self.on_output)
        else:
            # Create our own session
            if not self.connect():
                return
            self.session.execute('uptime', on_stdout=self.on_output)
