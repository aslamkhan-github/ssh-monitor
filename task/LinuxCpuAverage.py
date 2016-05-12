import logging
import time
import pickle
import struct

from SShUtil import CreateSshSession, SendGraphitePayload

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class LinuxCpuAverage:

    def __init__(self, task):
        self.destination = (task.db_host, task.db_port)
        self.session = CreateSshSession(task)
        self.path = task.path

    def on_output(self, task, line):
        out = line.split()
        now = int(time.time())

        one = (self.path + '.cpu_average.1min', (now, out[-3].replace(',', '')))
        five = (self.path + '.cpu_average.5min',
                (now, out[-2].replace(',', '')))
        fiftheen = (self.path + '.cpu_average.15min',
                    (now, out[-1].replace(',', '')))

        package = [one, five, fiftheen]
        payload = pickle.dumps(package, protocol=2)
        header = struct.pack("!L", len(payload))

        if SendGraphitePayload(self.destination, header, payload):
            logger.info('Sent:\n%s', package)

    def execute(self):
        self.session.execute('uptime', on_stdout=self.on_output)
