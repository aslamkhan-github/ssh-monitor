import logging
import socket
import time
import pickle
import struct

from SShUtil import CreateSshSession, SendGraphitePayload

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class LinuxDiskUsage:

    def __init__(self, task):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.destination = (task.db_host, task.db_port)
        self.session = CreateSshSession(task)
        self.path = task.path
        if len(task.disks) == 0:
            logging.error("LinuxDiskUsage: No disk name list provided")
        self.disks = task.disks

    def on_output(self, task, line):
        if 'Permission denied' in line:
            return
        now = int(time.time())
        out = line.split()

        disk_name = out[0].split('/')[2]
        path = self.path + '.disk.' + disk_name
        free = (path + '.free', (now, out[1].replace('M', '')))
        used = (path + '.used', (now, out[2].replace('M', '')))
        total = (path + '.available', (now, out[3].replace('M', '')))
        percent = (path + '.used_percent',
                   (now, out[4].replace('M', '').replace('%', '')))

        payload = pickle.dumps([free, used, total, percent], protocol=2)
        header = struct.pack("!L", len(payload))

        if SendGraphitePayload(self.destination, header, payload):
            logger.info('Sent:\n%s', [free, used, total, percent])

    def execute(self):
        for disk in self.disks:
            self.session.execute('df -BM | grep {}'.format(disk),
                                 on_stdout=self.on_output)
