import logging
import socket
import time
import pickle
import struct
import traceback

from SShUtil import CreateSshSession, SendGraphitePayload

# logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class LinuxDiskUsage:

    def __init__(self, task):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.destination = (task.db_host, task.db_port)
        self.task = task
        if len(task.disks) == 0:
            logging.error("LinuxDiskUsage: No disk name list provided")

    def on_output(self, task, line):
        if 'Permission denied' in line:
            logger.error("Permission denied")
            return
        now = int(time.time())
        out = line.split()

        try:
            disk_name = out[5].replace('/', '_')
            path = self.task.path + '.disk.' + disk_name
            free = (path + '.free', (now, out[1].replace('M', '')))
            used = (path + '.used', (now, out[2].replace('M', '')))
            total = (path + '.available', (now, out[3].replace('M', '')))
            percent = (path + '.used_percent',
                    (now, out[4].replace('M', '').replace('%', '')))

            payload = pickle.dumps([free, used, total, percent], protocol=2)
            header = struct.pack("!L", len(payload))

            if SendGraphitePayload(self.destination, header, payload):
                logger.debug('Sent:\n%s', [free, used, total, percent])
        except:
            logger.error(traceback.format_exc)

    def execute(self):
        session = CreateSshSession(self.task)
        if not session:
            return
        for disk in self.task.disks:
            session.execute('df -BM | grep {}'.format(disk),
                            on_stdout=self.on_output)
